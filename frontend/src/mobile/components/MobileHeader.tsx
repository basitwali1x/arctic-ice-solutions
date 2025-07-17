import { Bell, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface MobileHeaderProps {
  currentUser: {
    name: string;
    role: string;
    location: string;
  };
}

export function MobileHeader({ currentUser }: MobileHeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Button variant="ghost" size="sm" className="p-2">
          <Menu className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Arctic Ice</h1>
          <p className="text-xs text-gray-500">{currentUser.name}</p>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <Button variant="ghost" size="sm" className="relative p-2">
          <Bell className="h-5 w-5" />
          <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs bg-red-500">
            3
          </Badge>
        </Button>
      </div>
    </header>
  );
}
