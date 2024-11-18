import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../@/components/ui/card';
import { Button } from '../../@/components/ui/button';
import { Input } from '../../@/components/ui/input';
import { Textarea } from '../../@/components/ui/textarea';
import { Upload } from 'lucide-react';

const OpinionRequestForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    department: '',
    priority: 'normal',
    attachments: []
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    // TODO: Implement API call to backend
    console.log('Submitting request:', formData);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-semibold">New Opinion Request</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Request Title</label>
            <Input
              placeholder="Enter request title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium">Description</label>
            <Textarea
              placeholder="Describe your request in detail"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full h-32"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Department</label>
            <Input
              placeholder="Select target department"
              value={formData.department}
              onChange={(e) => setFormData({...formData, department: e.target.value})}
              className="w-full"
            />
          </div>

          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-8 h-8 mb-2 text-gray-500" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">PDF, DOC, DOCX (MAX. 10MB)</p>
              </div>
              <input type="file" className="hidden" multiple />
            </label>
          </div>

          <Button type="submit" className="w-full">
            Submit Request
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default OpinionRequestForm;