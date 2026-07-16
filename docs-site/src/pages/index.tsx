import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

const userLinks = [
  {
    label: 'Search',
    title: 'Open the recall search app',
    text: 'Search official recall exports by medicine name, product code, lot, alert id, year, or date range.',
    url: 'https://mrueda.github.io/recallrx/app/',
  },
  {
    label: 'Understand',
    title: 'Read the user guide',
    text: 'Learn what badges, warnings, source links, country switching, and daily export dates mean.',
    url: '/recallrx/docs/usage/quickstart',
  },
  {
    label: 'Safety',
    title: 'Safety language',
    text: 'Use official source links for decisions and treat RecallRx as an index, not medical advice.',
    url: '/recallrx/docs/usage/safety-language',
  },
];

const developerLinks = [
  {
    label: 'Architecture',
    title: 'How it works',
    text: 'Review the static app, daily export pipeline, country-aware datasets, and source adapter boundaries.',
    url: '/recallrx/docs/technical-details/architecture',
  },
  {
    label: 'Schema',
    title: 'Normalized data model',
    text: 'Inspect the recall record contract used by the frontend and active country sources.',
    url: '/recallrx/docs/technical-details/data-schema',
  },
  {
    label: 'Extend',
    title: 'Add another country',
    text: 'Implement a new source adapter while keeping the browser app contract stable.',
    url: '/recallrx/docs/technical-details/source-adapters',
  },
];

const rows = [
  ['ES', 'AEMPS', 'R_21/2026', 'CN 755215'],
  ['PT', 'INFARMED', 'CI 054/CD', 'AIM 2621696'],
  ['FR', 'ANSM', 'Rappel produit', 'CIP 3400955062400'],
  ['AD', 'Salut', 'planned', 'source needed'],
];

export default function Home() {
  const logoUrl = useBaseUrl('/img/recallrx-logo.svg');

  return (
    <Layout
      title="RecallRx"
      description="Static, country-aware medicine recall search from official public sources">
      <main className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.heroGrid}>
            <div className={styles.copy}>
              <p className={styles.kicker}>RecallRx</p>
              <h1>Find medicine recalls from official public sources.</h1>
              <p className={styles.lede}>
                RecallRx publishes daily static exports from active regulatory
                sources in Spain, Portugal, and France. The docs explain how to
                interpret results and how to maintain or extend the collectors.
              </p>
              <div className={styles.actions}>
                <a className="button button--primary button--lg" href="https://mrueda.github.io/recallrx/app/">
                  Open live search
                </a>
                <a className="button button--secondary button--lg" href="#user-docs">
                  User guide
                </a>
                <a className="button button--secondary button--lg" href="#developer-docs">
                  Developer docs
                </a>
              </div>
            </div>

            <div className={styles.indexPanel} aria-label="RecallRx country index preview">
              <a className={styles.identity} href="https://mrueda.github.io/recallrx/app/">
                <img className={styles.logo} src={logoUrl} alt="RecallRx logo" />
                <span>Live recall index</span>
              </a>
              <div className={styles.tablePreview} aria-hidden="true">
                {rows.map((row) => (
                  <div className={styles.previewRow} key={row.join('-')}>
                    {row.map((cell) => (
                      <span key={cell}>{cell}</span>
                    ))}
                  </div>
                ))}
              </div>
              <div className={styles.statusRow}>
                <span className={styles.source}>official source</span>
                <span className={styles.static}>static JSON</span>
                <span className={styles.safe}>no safety claims</span>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.sections} id="user-docs" aria-labelledby="user-heading">
          <div className={styles.sectionHeader}>
            <p>User docs</p>
            <h2 id="user-heading">Use the app first.</h2>
          </div>
          <div className={styles.grid}>
            {userLinks.map((feature) => (
              <a className={styles.card} href={feature.url} key={feature.title}>
                <span>{feature.label}</span>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </a>
            ))}
          </div>
        </section>

        <section className={styles.sections} id="developer-docs" aria-labelledby="developer-heading">
          <div className={styles.sectionHeader}>
            <p>Developer docs</p>
            <h2 id="developer-heading">Maintain and extend RecallRx.</h2>
          </div>
          <div className={styles.grid}>
            {developerLinks.map((feature) => (
              <a className={styles.card} href={feature.url} key={feature.title}>
                <span>{feature.label}</span>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </a>
            ))}
          </div>
        </section>
      </main>
    </Layout>
  );
}
