# Project Setup Instructions

## Step-by-Step Guide

### 1. **Set up the `.env` file for Google API Key**

In the **backend** folder, create a `.env` file and add your Google API key like this:

```
GOOGLE_API_KEY=your_google_api_key_here
```

Make sure to replace `your_google_api_key_here` with your actual Google API key.

### 2. **Install Frontend Dependencies**

Open the terminal and run the following command to install the required packages:

```
npm install
```

This will install all the dependencies needed for the frontend.

### 3. **Start the Frontend**

After installing the dependencies, run the frontend in development mode:

```
npm run dev
```


This will start the frontend server and make it available on the designated port (usually `localhost:3000` or similar).

### 4. **Set up the Backend (Virtual Environment)**

Open another terminal window in the **backend** folder. Create and activate the virtual environment with the following commands:

For **Linux/MacOS**:

```
python3 -m venv venv  
source venv/bin/activate
```

For **Windows - powershell**:

```
python -m venv venv  
.\venv\Scripts\activate.ps1
```

This will set up the virtual environment for the backend.

### 5. **Install Backend Dependencies**

Inside the virtual environment, install the required Python dependencies:

```
pip install -r requirements.txt
```

This will install all the backend dependencies listed in the `requirements.txt` file.

### 6. **Run the Backend Server**

Now that the virtual environment is activated and dependencies are installed, run the backend server with:

```
uvicorn main:app --reload
```

This will start the backend server in development mode with hot reloading, making it available at `localhost:8000`.

### 7. **Access the Application**

Once both servers (frontend and backend) are running, you can open the application by visiting the frontend URL (typically `localhost:3000`) in your web browser.

---

### Additional Notes (Optional):

- If you encounter errors related to missing `.env` file, ensure you have correctly created it and added the required Google API key.
- Ensure that both backend and frontend servers are running simultaneously for proper interaction between them.