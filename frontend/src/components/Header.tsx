import { Search, MapPin, LogOut } from 'lucide-react';
import { NotificationBell } from './NotificationBell';
import { useAuth } from '../contexts/AuthContext';

export function Header() {
  const { user, logout } = useAuth();

  const getLocationName = (locationId: string) => {
    const locationMap: { [key: string]: string } = {
      'loc_1': 'Leesville HQ',
      'loc_2': 'Lake Charles',
      'loc_3': 'Lufkin',
      'loc_4': 'Jasper'
    };
    return locationMap[locationId] || locationId;
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-semibold text-gray-800">
            Arctic Ice Solutions
          </h2>
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="h-4 w-4 mr-1" />
            {user?.location_id ? getLocationName(user.location_id) : 'Unknown Location'}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search..."
              autoComplete="off"
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <NotificationBell />

          <div className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 rounded-lg p-2 transition-colors duration-200" onClick={logout} title="Click to logout">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
              {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
            </div>
            <span className="text-sm font-medium text-gray-700">{user?.full_name}</span>
          </div>

          <button 
            onClick={logout}
            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200 border border-transparent hover:border-red-200"
            title="Logout"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
