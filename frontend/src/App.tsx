import React from 'react'
import { Outlet } from 'react-router-dom'
import { Navigation } from './components/navigation'
import Dashboard from 'components/Dashboard';
import OpinionsList from 'components/OpinionsList';

const App = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="container mx-auto py-6">
        <Outlet />
      </main>
    </div>
  )
}
// src/App.tsx

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: '/',
        element: <Dashboard />
      },
      {
        path: '/',
        element: <OpinionsList />
      },
      {
        path: '/',
        element: <OpinionRequestForm />
      }
    ]
  }
]);
export default App