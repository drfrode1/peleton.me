import type { QueryClient } from '@tanstack/react-query';
import { createRootRouteWithContext, Link, Outlet } from '@tanstack/react-router';

export interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  return (
    <div className="app-shell">
      {/* Top Announcement Bar */}
      <div className="announcement">
        <div className="announcement-inner">
          <span className="announcement-dot" />
          A little more movement. A lot more life.
          <span className="announcement-location">Built for Norway</span>
        </div>
      </div>

      {/* Main Brand Header */}
      <header className="site-header">
        <div className="site-header-inner">
          <Link className="brand" to="/" aria-label="Peleton home, with Tour of Norway">
            <img
              className="brand-logo"
              src="/tour-of-norway-logo.png"
              alt="Tour of Norway"
              width={118}
              height={48}
            />
            <span className="brand-divider" aria-hidden="true" />
            <span className="wordmark" aria-hidden="true">
              peleton<span className="wordmark-period">.</span>
            </span>
          </Link>

          <nav className="main-nav" aria-label="Main navigation">
            <Link to="/" className="nav-link" activeProps={{ className: 'nav-link active' }} activeOptions={{ exact: true }}>
              Home
            </Link>
            <Link to="/leaderboard" className="nav-link" activeProps={{ className: 'nav-link active' }}>
              Leaderboard
            </Link>
            <Link to="/health-value" className="nav-link" activeProps={{ className: 'nav-link active' }}>
              Health value
            </Link>
          </nav>

          <div className="account-actions">
            <Link className="button button-primary header-cta" to="/settings">
              Settings <span aria-hidden="true">↗</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main>
        <Outlet />
      </main>

      {/* Tour of Norway Footer */}
      <footer className="site-footer">
        <div className="site-footer-inner">
          <div className="footer-brand">
            <span className="footer-logo">
              <img src="/tour-of-norway-logo.png" alt="Tour of Norway" width={118} height={48} />
            </span>
            <Link className="wordmark footer-wordmark" to="/" aria-label="Peleton home">
              peleton<span className="wordmark-period">.</span>
            </Link>
            <p>Good things happen when we move together.</p>
          </div>

          <nav className="footer-nav" aria-label="Footer navigation">
            <Link to="/">Home</Link>
            <Link to="/leaderboard">Leaderboard</Link>
            <Link to="/health-value">Health value</Link>
          </nav>
        </div>

        <div className="footer-bottom">
          <span className="footer-note">Made for the long ride&nbsp; · &nbsp;Norway</span>
        </div>
      </footer>
    </div>
  );
}
