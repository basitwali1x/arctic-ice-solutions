import { NavLink } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { BookOpen, Award, Shield, TrendingUp } from 'lucide-react';

const navigationItems = [
  {
    title: 'Training Modules',
    href: '/employee/training',
    icon: BookOpen,
  },
  {
    title: 'Certifications',
    href: '/employee/certifications',
    icon: Award,
  },
  {
    title: 'Safety Protocols',
    href: '/employee/safety',
    icon: Shield,
  },
  {
    title: 'Progress Tracking',
    href: '/employee/progress',
    icon: TrendingUp,
  },
];

export function EmployeeNavigation() {
  return (
    <nav className="w-64 border-r bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
            Employee Portal
          </h2>
          <div className="space-y-1">
            {navigationItems.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "flex items-center rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground",
                    isActive ? "bg-accent text-accent-foreground" : "transparent"
                  )
                }
              >
                <item.icon className="mr-2 h-4 w-4" />
                {item.title}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
