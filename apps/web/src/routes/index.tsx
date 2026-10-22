import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: HomeComponent,
});

function HomeComponent() {
  const impactStats = [
    { value: '48,210', label: 'active minutes' },
    { value: '14,890', label: 'kilometres moved' },
    { value: '1,240', label: 'people moving across 42 companies' },
  ];

  return (
    <>
      {/* Home Hero Section */}
      <section className="home-hero">
        <div className="hero-inner">
          <div className="hero-copy">
            <p className="eyebrow">
              <span className="eyebrow-line" /> THE GOOD-MOVE CLUB
            </p>
            <h1 aria-label="Find your own pace.">
              Find your<br />own <em>pace.</em>
            </h1>
            <p className="hero-description">
              Every walk, ride and run adds up. Make your everyday journey
              count — for you, your community and the place we call home.
            </p>
            <div className="hero-actions">
              <Link className="button button-primary" to="/settings">
                Find your place <span aria-hidden="true">↗</span>
              </Link>
              <Link className="text-link" to="/leaderboard">
                See what we&apos;re moving <span aria-hidden="true">→</span>
              </Link>
            </div>
            <div className="hero-social-proof">
              <div className="avatar-stack" aria-hidden="true">
                <span>IN</span><span>MK</span><span>AS</span><span>+</span>
              </div>
              <p>
                <strong>1,240 people</strong> made a good move this month
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <div className="page-shell">
        <section className="impact-section" aria-labelledby="impact-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                <span className="eyebrow-line" /> THE PELOTON EFFECT
              </p>
              <h2 id="impact-title">Better, <em>together.</em></h2>
            </div>
            <p className="section-intro">
              It&apos;s not about being the fastest. It&apos;s about showing up,
              finding your rhythm and making room for one more.
            </p>
          </div>

          <div className="impact-grid">
            {impactStats.map((stat, index) => (
              <article className="impact-card" key={stat.label}>
                <span className="impact-index">0{index + 1}</span>
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
              </article>
            ))}
          </div>

          <Link className="impact-link" to="/leaderboard">
            The latest good moves <span aria-hidden="true">↗</span>
          </Link>
          <p className="impact-source">
            Powered by connected Strava commuter activities, Statens Vegvesen traffic telemetry, and MET Norway data.
          </p>
        </section>

        {/* Bergen Start Photo */}
        <figure className="bergen-photo">
          <img
            src="/bergen-start.jpg"
            alt="Crowds line the street at the race start in Bergen, with the colourful Bryggen wooden houses behind."
            loading="lazy"
          />
        </figure>
      </div>

      {/* Invitation Band */}
      <section className="invitation-band">
        <div className="invitation-inner">
          <div>
            <p className="eyebrow eyebrow-light">
              <span className="eyebrow-line" /> YOUR NEXT CHAPTER
            </p>
            <h2 aria-label="There's room in the peleton.">
              There&apos;s room<br />in the <em>peleton.</em>
            </h2>
          </div>
          <Link className="button button-primary" to="/settings">
            Come along <span aria-hidden="true">↗</span>
          </Link>
        </div>
        <span className="invitation-decoration" aria-hidden="true">P</span>
      </section>
    </>
  );
}
