import './globals.css';
import Navigation from './components/Navigation';

export const metadata = {
  title: 'Jimmy Bot Dashboard',
  description: 'A modern dashboard for managing Jimmy Bot users, messages, and platform health.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        {children}
      </body>
    </html>
  );
}
