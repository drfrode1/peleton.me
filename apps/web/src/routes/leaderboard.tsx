import { useState } from 'react';
import { createFileRoute, Link } from '@tanstack/react-router';

type Scope = 'companies' | 'sectors' | 'regions';

export const Route = createFileRoute('/leaderboard')({
  component: LeaderboardComponent,
});

function LeaderboardComponent() {
  const [activeScope, setActiveScope] = useState<Scope>('companies');

  const jerseys = [
    {
      key: 'distance',
      className: 'jersey-green',
      image: '/jerseys/distance.webp',
      imageAlt: 'Distance leader jersey',
      name: 'The Distance Jersey',
      category: 'KM PER PARTICIPANT',
      winner: 'Equinor ASA',
      value: '42.5 km / person',
    },
    {
      key: 'all_weather',
      className: 'jersey-blue',
      image: '/jerseys/weather.webp',
      imageAlt: 'All-weather jersey',
      name: 'The All-weather Jersey',
      category: 'RAIN OR SHINE',
      winner: 'Stavanger Kommune',
      value: '9.2 wet commutes / person',
    },
    {
      key: 'region',
      className: 'jersey-orange',
      image: '/jerseys/region.webp',
      imageAlt: 'Region jersey',
      name: 'The Region Jersey',
      category: 'REGIONAL MOVEMENT',
      winner: 'Rogaland',
      value: '28,450 km moved',
    },
    {
      key: 'sector',
      className: 'jersey-sector',
      image: '/jerseys/sector.webp',
      imageAlt: 'Sector jersey',
      name: 'The Sector Jersey',
      category: 'INDUSTRY SECTOR',
      winner: 'Energy & Tech',
      value: '35,120 km moved',
    },
  ];

  const scopeMetadata: Record<Scope, { heading: string; label: string }> = {
    companies: { heading: 'Companies on the move', label: 'COMPANY' },
    sectors: { heading: 'Sectors finding their stride', label: 'SECTOR' },
    regions: { heading: 'Regions across Norway', label: 'REGION' },
  };

  const companyRows = [
    { rank: 1, name: 'Equinor ASA', sector: 'Energy & Offshore', region: 'Stavanger', participants: 412, km: '17,510', kmPer: '42.5', wetRides: '8.7' },
    { rank: 2, name: 'Aker BP', sector: 'Energy', region: 'Stavanger / Forus', participants: 285, km: '11,400', kmPer: '40.0', wetRides: '7.4' },
    { rank: 3, name: 'Stavanger Kommune', sector: 'Public Sector', region: 'Rogaland', participants: 360, km: '12,960', kmPer: '36.0', wetRides: '9.2' },
    { rank: 4, name: 'Bouvet Norge', sector: 'Technology', region: 'Stavanger / Oslo', participants: 198, km: '6,930', kmPer: '35.0', wetRides: '6.8' },
    { rank: 5, name: 'Laerdal Medical', sector: 'Healthcare & Life Sciences', region: 'Stavanger', participants: 165, km: '5,610', kmPer: '34.0', wetRides: '6.1' },
    { rank: 6, name: 'DNB Bank ASA', sector: 'Finance', region: 'National', participants: 310, km: '9,920', kmPer: '32.0', wetRides: '5.9' },
  ];

  const sectorRows = [
    { rank: 1, name: 'Energy & Tech', sector: '14 companies', region: 'National', participants: 895, km: '35,120', kmPer: '39.2', wetRides: '7.9' },
    { rank: 2, name: 'Public Sector & Municipalities', sector: '8 organizations', region: 'National', participants: 620, km: '21,700', kmPer: '35.0', wetRides: '8.4' },
    { rank: 3, name: 'Consulting & Software', sector: '12 companies', region: 'National', participants: 430, km: '14,620', kmPer: '34.0', wetRides: '6.5' },
    { rank: 4, name: 'Healthcare & Bio', sector: '6 companies', region: 'National', participants: 290, km: '9,280', kmPer: '32.0', wetRides: '5.8' },
  ];

  const regionRows = [
    { rank: 1, name: 'Rogaland (Stavanger / Forus / Sandnes)', sector: '22 workplaces', region: 'West Coast', participants: 1240, km: '48,210', kmPer: '38.9', wetRides: '8.8' },
    { rank: 2, name: 'Vestland (Bergen / Bryggen)', sector: '12 workplaces', region: 'West Coast', participants: 680, km: '23,800', kmPer: '35.0', wetRides: '11.2' },
    { rank: 3, name: 'Oslo & Viken', sector: '16 workplaces', region: 'Eastern Norway', participants: 790, km: '26,070', kmPer: '33.0', wetRides: '5.2' },
  ];

  const activeRows = activeScope === 'companies' ? companyRows : activeScope === 'sectors' ? sectorRows : regionRows;

  return (
    <div className="page-shell subpage-shell">
      {/* Header */}
      <section className="settings-heading">
        <div>
          <p className="eyebrow">
            <span className="eyebrow-line" /> THE TOUR OF NORWAY LEADERBOARD
          </p>
          <h1>
            National<br /><em>leaderboard.</em>
          </h1>
          <p className="hero-description">
            Celebrating the workplaces, sectors and regions translating daily commutes into national health and emission savings.
          </p>
        </div>
      </section>

      {/* Jersey Cards Grid — 4 Columns */}
      <section className="jersey-section" aria-labelledby="jersey-title">
        <div className="jersey-section-heading">
          <div>
            <p className="eyebrow"><span className="eyebrow-line" /> CURRENT CLASSIFICATION</p>
            <h2 id="jersey-title">Four ways to <em>wear the win.</em></h2>
          </div>
          <span className="week-label">LAST 30 DAYS</span>
        </div>

        <div className="jersey-grid" aria-label="Current Jersey Leaders">
          {jerseys.map((jersey) => (
            <article key={jersey.key} className={`jersey-card ${jersey.className}`}>
              <div className="jersey-card-top">
                <span className="jersey-event">{jersey.category}</span>
              </div>
              <img src={jersey.image} alt={jersey.imageAlt} className="jersey-image" loading="lazy" />
              <h3>{jersey.name}</h3>
              <div className="jersey-footer">
                <p className="jersey-winner">{jersey.winner}</p>
                <p className="jersey-detail">{jersey.value}</p>
              </div>
              <span className="jersey-ribbon" aria-hidden="true">01</span>
            </article>
          ))}
        </div>
      </section>

      {/* Collective Leaderboard Panel — Full Width 100% Spanning all 4 Jerseys */}
      <section className="leaderboard-board collective-board" style={{ width: '100%', marginTop: '40px' }} aria-labelledby="rankings-title">
        <div className="board-topline">
          <div className="board-tabs" role="group" aria-label="Leaderboard scope">
            {(['companies', 'sectors', 'regions'] as Scope[]).map((scopeKey) => (
              <button
                key={scopeKey}
                type="button"
                className={`board-tab ${activeScope === scopeKey ? 'selected' : ''}`}
                onClick={() => setActiveScope(scopeKey)}
              >
                {scopeKey[0].toUpperCase() + scopeKey.slice(1)}
              </button>
            ))}
          </div>
          <span className="board-period">COLLECTIVE MOVEMENT · LAST 30 DAYS</span>
        </div>

        <div className="board-heading">
          <div>
            <p className="eyebrow"><span className="eyebrow-line" /> THE PELOTON CLASSIFICATION</p>
            <h2 id="rankings-title">{scopeMetadata[activeScope].heading}</h2>
          </div>
          <p>
            Measured together, ranked together.<br />Personal activity stays personal.
          </p>
        </div>

        <div className="collective-table-wrap">
          <table className="collective-table">
            <thead>
              <tr>
                <th scope="col" style={{ width: '80px' }}>PLACE</th>
                <th scope="col">{scopeMetadata[activeScope].label}</th>
                <th scope="col" style={{ textAlign: 'right' }}>PARTICIPANTS</th>
                <th scope="col" style={{ textAlign: 'right' }}>KM / PARTICIPANT</th>
                <th scope="col" style={{ textAlign: 'right' }}>WET COMMUTES / PERSON</th>
              </tr>
            </thead>
            <tbody>
              {activeRows.map((row) => (
                <tr key={row.name}>
                  <td className="collective-rank">{row.rank < 10 ? `0${row.rank}` : row.rank}</td>
                  <th scope="row">
                    <span className="collective-name">{row.name}</span>
                    <span className="collective-subtitle">{row.sector} {row.region ? `· ${row.region}` : ''}</span>
                  </th>
                  <td style={{ textAlign: 'right' }}>{row.participants}</td>
                  <td className="collective-distance" style={{ textAlign: 'right' }}>
                    {row.kmPer} <small>km</small>
                  </td>
                  <td className="collective-weather" style={{ textAlign: 'right' }}>
                    {row.wetRides}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="board-footer">
          <p>Rankings use group totals and averages only. Participation is voluntary; no individual names, times or routes are shown.</p>
          <Link to="/settings" className="text-link">See your settings <span aria-hidden="true">→</span></Link>
        </div>
      </section>

      {/* Weather Telemetry Insights Note */}
      <section className="weather-section">
        <h2>Weather resilience in Norwegian corridors.</h2>
        <div className="weather-bands">
          <article className="weather-band-card">
            <h3>Rain Resilience</h3>
            <ul>
              <li><span>&lt; 2 mm rain</span><strong>38.4 km/wk</strong></li>
              <li><span>2 – 10 mm rain</span><strong>36.8 km/wk</strong></li>
              <li><span>&gt; 10 mm heavy rain</span><strong>34.2 km/wk</strong></li>
            </ul>
            <p>Norwegian commuters sustain <strong>89% of cycling volume</strong> even during wet days exceeding 10mm precipitation.</p>
          </article>

          <article className="weather-band-card">
            <h3>Wind Resilience</h3>
            <ul>
              <li><span>&lt; 5 m/s breeze</span><strong>40.1 km/wk</strong></li>
              <li><span>5 – 10 m/s moderate</span><strong>37.5 km/wk</strong></li>
              <li><span>&gt; 10 m/s coastal wind</span><strong>33.8 km/wk</strong></li>
            </ul>
            <p>Lakehouse data links MET Frost anemometer telemetry to corridor Strava segments in Rogaland and Vestland.</p>
          </article>
        </div>
      </section>
    </div>
  );
}
