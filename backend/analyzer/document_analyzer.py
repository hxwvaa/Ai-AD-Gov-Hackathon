import spacy
import pytesseract
from typing import Dict, List, Optional
import fitz  # PyMuPDF
from transformers import pipeline
import numpy as np
from dataclasses import dataclass
import json
import logging
from pathlib import Path

@dataclass
class AnalysisResult:
    """Data class to store document analysis results"""
    document_id: str
    title: str
    summary: str
    topics: List[str]
    key_points: List[str]
    entities: Dict[str, List[str]]
    relevance_score: float
    department_suggestions: List[str]
    references: List[Dict]

class DocumentAnalyzer:
    def __init__(self):
        # Load SpaCy model for NER and text processing
        self.nlp = spacy.load("en_core_web_lg")
        
        # Initialize transformers pipeline for summarization
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Initialize zero-shot classification for topic detection
        self.topic_classifier = pipeline("zero-shot-classification")
        
        # Predefined topics based on department policies
        self.policy_topics = [
            "Finance", "Legal", "Human Resources", "Operations",
            "Information Technology", "Public Relations", "Strategy"
        ]
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or images within PDF"""
        try:
            text = ""
            # Open PDF document
            doc = fitz.open(file_path)
            
            for page in doc:
                # Get text from PDF
                text += page.get_text()
                
                # Handle images in PDF
                for img in page.get_images():
                    pix = fitz.Pixmap(doc, img[0])
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    # Convert to image and extract text
                    img_text = pytesseract.image_to_string(pix.tobytes())
                    text += "\n" + img_text
                    
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            raise

    def analyze_document(self, file_path: str, document_id: str) -> AnalysisResult:
        """Main method to analyze document and return structured results"""
        try:
            # Extract text from document
            text = self.extract_text(file_path)
            
            # Process with SpaCy
            doc = self.nlp(text)
            
            # Generate summary
            summary = self._generate_summary(text)
            
            # Extract topics
            topics = self._classify_topics(text)
            
            # Extract key points
            key_points = self._extract_key_points(doc)
            
            # Named Entity Recognition
            entities = self._extract_entities(doc)
            
            # Calculate department relevance
            dept_suggestions = self._suggest_departments(text, topics)
            
            # Find relevant references
            references = self._find_references(doc)
            
            # Calculate overall relevance score
            relevance_score = self._calculate_relevance(topics, entities)
            
            return AnalysisResult(
                document_id=document_id,
                title=self._extract_title(doc),
                summary=summary,
                topics=topics,
                key_points=key_points,
                entities=entities,
                relevance_score=relevance_score,
                department_suggestions=dept_suggestions,
                references=references
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing document: {str(e)}")
            raise

    def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of the document"""
        chunks = self._chunk_text(text, max_length=1024)
        summaries = []
        
        for chunk in chunks:
            summary = self.summarizer(chunk, max_length=150, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        return " ".join(summaries)

    def _classify_topics(self, text: str) -> List[str]:
        """Classify text into predefined policy topics"""
        result = self.topic_classifier(
            text,
            candidate_labels=self.policy_topics,
            multi_label=True
        )
        
        # Filter topics with confidence > 0.3
        return [label for score, label in zip(result['scores'], result['labels']) 
                if score > 0.3]

    def _extract_key_points(self, doc) -> List[str]:
        """Extract key points from the document"""
        key_points = []
        
        # Extract sentences with important entities or key phrases
        for sent in doc.sents:
            # Check for key indicators of important points
            if any(token.is_title for token in sent) or \
               any(ent.label_ in ['ORG', 'LAW', 'DATE'] for ent in sent.ents):
                key_points.append(sent.text.strip())
        
        return list(set(key_points))[:10]  # Return top 10 unique key points

    def _suggest_departments(self, text: str, topics: List[str]) -> List[str]:
        """Suggest relevant departments based on content analysis"""
        department_keywords = {
            "Legal": ["law", "regulation", "compliance", "legal", "rights"],
            "Finance": ["budget", "cost", "revenue", "financial", "funding"],
            "HR": ["employee", "staff", "training", "recruitment", "personnel"],
            # Add more department keywords as needed
        }
        
        suggestions = []
        doc = self.nlp(text.lower())
        
        for dept, keywords in department_keywords.items():
            if any(keyword in doc.text for keyword in keywords):
                suggestions.append(dept)
                
        return list(set(suggestions))

    def _find_references(self, doc) -> List[Dict]:
        """Find references to existing policies or previous opinions"""
        references = []
        reference_patterns = [
            "policy", "regulation", "directive", "circular",
            "opinion", "decision", "ruling"
        ]
        
        for sent in doc.sents:
            for pattern in reference_patterns:
                if pattern in sent.text.lower():
                    references.append({
                        "type": pattern,
                        "text": sent.text.strip(),
                        "context": self._get_context(sent)
                    })
        
        return references

    def _calculate_relevance(self, topics: List[str], entities: Dict) -> float:
        """Calculate overall relevance score"""
        # Simple scoring based on number of relevant topics and entities
        topic_score = len(topics) / len(self.policy_topics)
        entity_score = min(len(entities) / 10, 1.0)  # Cap at 1.0
        
        return (topic_score + entity_score) / 2

    def _chunk_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks of maximum length"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from the document"""
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        return {k: list(set(v)) for k, v in entities.items()}

    def _extract_title(self, doc) -> str:
        """Extract document title from first few sentences"""
        for sent in list(doc.sents)[:3]:
            if len(sent.text.split()) <= 20 and sent.text.strip():
                return sent.text.strip()
        return "Untitled Document"

if __name__ == "__main__":
    # Example usage
    analyzer = DocumentAnalyzer()
    
    def process_document(file_path: str, document_id: str) -> None:
        try:
            result = analyzer.analyze_document(file_path, document_id)
            
            # Save results to JSON
            output_path = Path(f"analysis_results/{document_id}.json")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(dataclasses.asdict(result), f, indent=2)
                
            print(f"Analysis completed successfully for document {document_id}")
            
        except Exception as e:
            print(f"Error processing document {document_id}: {str(e)}")