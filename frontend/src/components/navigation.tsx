import React from 'react';
import { Link } from 'react-router-dom';
import { FilePlus, LayoutDashboard, FileText } from 'lucide-react';

export const Navigation = () => {
  return (
    <nav className="border-b">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-semibold">
              OpinionForge
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            <Link 
              to="/new-request" 
              className="flex items-center space-x-2 px-4 py-2 rounded-md hover:bg-secondary"
            >
              <FilePlus size={20} />
              <span>New Request</span>
            </Link>
            
            <Link 
              to="/dashboard" 
              className="flex items-center space-x-2 px-4 py-2 rounded-md hover:bg-secondary"
            >
              <LayoutDashboard size={20} />
              <span>Dashboard</span>
            </Link>
            
            <Link 
              to="/opinions" 
              className="flex items-center space-x-2 px-4 py-2 rounded-md hover:bg-secondary"
            >
              <FileText size={20} />
              <span>Opinions</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;