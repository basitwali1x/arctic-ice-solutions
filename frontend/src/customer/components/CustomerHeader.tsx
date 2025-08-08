import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Menu, User, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface CustomerHeaderProps {
  currentUser: {
    name: string;
    role: string;
    location: string;
  };
}

export function CustomerHeader({ currentUser }: CustomerHeaderProps) {
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Arctic Ice Solutions</h1>
          <p className="text-sm text-gray-600 dark:text-gray-300">{currentUser.name}</p>
        </div>
        <div className="relative">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowMenu(!showMenu)}
            className="p-2"
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          {showMenu && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-50">
              <div className="p-2 space-y-1">
                <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/customer/dashboard'); setShowMenu(false); }}>
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </Button>
                <hr className="my-2 border-gray-200 dark:border-gray-600" />
                <Button variant="ghost" className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
