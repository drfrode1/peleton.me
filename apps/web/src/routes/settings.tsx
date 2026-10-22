import { useState, useEffect } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ShieldCheck, ArrowRight, CheckCircle2 } from 'lucide-react';
import { CompanyPicker } from '../components/CompanyPicker';
import { connectStrava, disconnectStrava } from '../lib/api/strava';
import { stravaStatusQueryOptions } from '../lib/queries/strava';
import { registerCompany, type CompanySearchItem } from '../lib/api/companies';

const oauthMessages: Record<string, string> = {
  connected: 'Your Strava account has been connected successfully.',
  denied: 'Strava authorization was cancelled.',
  'scope-required': 'Please approve read access to your activities to enable syncing.',
  error: 'Could not connect Strava. Please check your credentials and try again.',
};

export const Route = createFileRoute('/settings')({
  loader: ({ context: { queryClient } }) =>
    queryClient.ensureQueryData(stravaStatusQueryOptions()),
  component: SettingsComponent,
});

function SettingsComponent() {
  const queryClient = useQueryClient();
  const { data: stravaStatus, isLoading: stravaLoading } = useQuery(stravaStatusQueryOptions());

  const [oauthResult] = useState(() =>
    typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('strava') : null
  );
  const [selectedCompany, setSelectedCompany] = useState<CompanySearchItem | null>(null);
  const [companyMessage, setCompanyMessage] = useState('');
  const [stravaFeedback, setStravaFeedback] = useState('');
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    if (oauthResult && typeof window !== 'undefined') {
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [oauthResult]);

  async function handleConnectStrava() {
    setIsBusy(true);
    setStravaFeedback('');
    try {
      const result = await connectStrava();
      window.location.assign(result.authorization_url);
    } catch (err) {
      setStravaFeedback(err instanceof Error ? err.message : 'Could not start Strava authorization.');
      setIsBusy(false);
    }
  }

  async function handleDisconnectStrava() {
    setIsBusy(true);
    setStravaFeedback('');
    try {
      const result = await disconnectStrava();
      await queryClient.invalidateQueries({ queryKey: ['strava', 'status'] });
      setStravaFeedback(
        result.provider_revoked
          ? 'Strava disconnected and token access revoked.'
          : 'Saved tokens deleted. Please verify revocation in your Strava account settings.'
      );
    } catch (err) {
      setStravaFeedback(err instanceof Error ? err.message : 'Could not disconnect Strava.');
    } finally {
      setIsBusy(false);
    }
  }

  async function handleSaveCompany() {
    if (!selectedCompany) return;
    setIsBusy(true);
    setCompanyMessage('');
    try {
      await registerCompany({
        org_number: selectedCompany.org_number,
        name: selectedCompany.name,
        postal_code: selectedCompany.postal_code,
        company_type: selectedCompany.company_type,
        company_category: selectedCompany.company_category,
      });
      setCompanyMessage('Organization affiliation saved.');
    } catch (err) {
      setCompanyMessage(err instanceof Error ? err.message : 'Could not save company.');
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="page-shell subpage-shell">
      {/* Page Header */}
      <section className="settings-heading">
        <div>
          <p className="eyebrow">
            <span className="eyebrow-line" /> YOUR SPACE, YOUR CHOICES
          </p>
          <h1>
            Personal<br /><em>settings.</em>
          </h1>
          <p className="hero-description">
            Keep your account details up to date and choose the activity services you want to connect.
          </p>
        </div>
        <span className="settings-prototype-badge">SIGNED IN</span>
      </section>

      {/* OAuth callback status alert */}
      {(stravaFeedback || (oauthResult && oauthMessages[oauthResult])) && (
        <div className="data-state" role="alert">
          <p className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-blue" />
            <span>{stravaFeedback || oauthMessages[oauthResult!]}</span>
          </p>
        </div>
      )}

      {/* Account Details Panel */}
      <section className="settings-panel" aria-labelledby="account-settings-title">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow"><span className="eyebrow-line" /> ACCOUNT</p>
            <h2 id="account-settings-title">Your details</h2>
          </div>
        </div>

        <div className="settings-detail-grid">
          <div className="settings-detail">
            <span>NAME</span>
            <strong>Dev Commuter</strong>
          </div>
          <div className="settings-detail">
            <span>EMAIL</span>
            <strong>dev@peleton.me</strong>
          </div>
          <div className="settings-detail">
            <span>SIGN-IN PROVIDER</span>
            <strong>Google OAuth</strong>
            <small>Managed via Neon Better Auth</small>
          </div>
          <div className="settings-detail">
            <span>USER ID</span>
            <strong className="font-mono text-sm">00000000-0000-0000-0000-000000000001</strong>
          </div>
        </div>
      </section>

      {/* Brønnøysund Organization Panel */}
      <section className="settings-panel" aria-labelledby="company-settings-title">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow"><span className="eyebrow-line" /> BRØNNØYSUND REGISTRY</p>
            <h2 id="company-settings-title">Your workplace</h2>
            <p className="settings-section-description">
              Search the official Norwegian register to associate your active commuting with your company.
            </p>
          </div>
        </div>

        <div style={{ marginTop: '24px' }}>
          <CompanyPicker
            id="settings-company"
            label="Search employer or organization"
            selected={selectedCompany}
            onSelect={(company) => {
              setSelectedCompany(company);
              setCompanyMessage('');
            }}
          />

          {selectedCompany && (
            <div style={{ marginTop: '16px' }}>
              <button
                type="button"
                disabled={isBusy}
                onClick={() => void handleSaveCompany()}
                className="button button-primary"
              >
                {isBusy ? 'Saving...' : 'Save Organization'} <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          )}

          {companyMessage && (
            <p className="text-sm font-semibold text-blue flex items-center gap-2" style={{ marginTop: '12px' }}>
              <CheckCircle2 className="w-4 h-4 text-primary" /> {companyMessage}
            </p>
          )}
        </div>
      </section>

      {/* Private Activity & Strava Integration Panel */}
      <section className="settings-panel" aria-labelledby="connections-title">
        <div className="settings-section-heading">
          <div>
            <p className="eyebrow"><span className="eyebrow-line" /> PRIVATE ACTIVITY</p>
            <h2 id="connections-title">Connected services</h2>
          </div>
          <span className="connections-private flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4" /> ONLY YOU CAN SEE THIS
          </span>
        </div>

        <div className="settings-provider-list">
          {/* Strava Provider */}
          <div className="settings-provider">
            <div className="provider-mark strava-mark">S</div>
            <div className="settings-provider-copy">
              <strong>Strava</strong>
              <span>
                {stravaLoading
                  ? 'Checking connection status...'
                  : stravaStatus?.connected
                  ? `Connected · Athlete ID: ${stravaStatus.athlete_id}`
                  : 'Read access to all your activities (read, activity:read_all)'}
              </span>
            </div>

            {stravaStatus?.connected ? (
              <button
                type="button"
                disabled={isBusy}
                onClick={() => void handleDisconnectStrava()}
                className="button-outline"
                style={{ cursor: 'pointer' }}
              >
                {isBusy ? 'Disconnecting...' : 'Disconnect'}
              </button>
            ) : (
              <button
                type="button"
                disabled={isBusy || stravaLoading}
                onClick={() => void handleConnectStrava()}
                className="button button-primary"
                style={{ cursor: 'pointer' }}
              >
                {isBusy ? 'Connecting...' : 'Connect Strava'} <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            )}
          </div>

          {/* Garmin Provider Placeholder */}
          <div className="settings-provider" style={{ opacity: 0.65 }}>
            <div className="provider-mark garmin-mark">G</div>
            <div className="settings-provider-copy">
              <strong>Garmin Connect</strong>
              <span>Direct Garmin device sync coming soon.</span>
            </div>
            <span className="demo-badge">COMING SOON</span>
          </div>
        </div>

        {/* Privacy Invariant Banner */}
        <div className="settings-privacy-note">
          <span aria-hidden="true">✳</span>
          <p>
            <strong>Your individual activity is never shown on the leaderboard.</strong><br />
            Only aggregated company, sector and regional totals contribute to shared rankings.
          </p>
        </div>
        <p className="connections-disclaimer">
          Strava tokens are encrypted using AES-256-GCM and stored securely server-side.
          Disconnecting revokes token access and deletes saved credentials.
        </p>
      </section>
    </div>
  );
}
