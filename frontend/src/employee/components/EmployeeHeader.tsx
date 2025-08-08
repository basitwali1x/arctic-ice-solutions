import { ThemeToggle } from '../../components/ThemeToggle';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { LogOut, Snowflake } from 'lucide-react';

export function EmployeeHeader() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="flex items-center space-x-2">
          <Snowflake className="h-6 w-6 text-blue-600" />
          <span className="font-bold text-xl">Arctic Ice Solutions</span>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <span className="text-sm text-muted-foreground">
            Welcome, {user?.username}
          </span>
          <ThemeToggle />
          <Button variant="outline" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
