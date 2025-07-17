import { Search, MapPin } from 'lucide-react';
import { NotificationBell } from './NotificationBell';

interface HeaderProps {
  currentUser: {
    name: string;
    role: string;
    location: string;
  };
}

export function Header({ currentUser }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-semibold text-gray-800">
            Arctic Ice Solutions
          </h2>
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="h-4 w-4 mr-1" />
            {currentUser.location}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <NotificationBell />

          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
              {currentUser.name.split(' ').map(n => n[0]).join('')}
            </div>
            <span className="text-sm font-medium text-gray-700">{currentUser.name}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
