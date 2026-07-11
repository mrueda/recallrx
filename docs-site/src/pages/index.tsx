import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

const userLinks = [
  {
    label: 'Search',
    title: 'Open the recall search app',
    text: 'Search by medicine name, product code, lot, alert id, year, or date range.',
    url: 'https://mrueda.github.io/openrecall/app/',
  },
  {
    label: 'Understand',
    title: 'Read the user guide',
    text: 'Learn what the results mean, how source links work, and what OpenRecall does not claim.',
    url: '/openrecall/docs/usage/quickstart',
  },
  {
    label: 'Safety',
    title: 'Safety language',
    text: 'Use official AEMPS links for decisions and treat OpenRecall as an index, not medical advice.',
    url: '/openrecall/docs/usage/safety-language',
  },
];

const developerLinks = [
  {
    label: 'Architecture',
    title: 'How it works',
    text: 'Review the static app, country-aware datasets, and source adapter boundaries.',
    url: '/openrecall/docs/technical-details/architecture',
  },
  {
    label: 'Schema',
    title: 'Normalized data model',
    text: 'Inspect the recall record contract used by the frontend and future country sources.',
    url: '/openrecall/docs/technical-details/data-schema',
  },
  {
    label: 'Extend',
    title: 'Add another country',
    text: 'Implement a new source adapter while keeping the browser app contract stable.',
    url: '/openrecall/docs/technical-details/source-adapters',
  },
];

const rows = [
  ['ES', 'AEMPS', 'R_21/2026', 'CN 755215'],
  ['US', 'FDA', 'planned', 'NDC'],
  ['UK', 'MHRA', 'planned', 'PL'],
  ['CA', 'Health Canada', 'planned', 'DIN'],
];

export default function Home() {
  const logoUrl = useBaseUrl('/img/openrecall-logo.svg');

  return (
    <Layout
      title="OpenRecall"
      description="Static, country-extensible medicine recall search">
      <main className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.heroGrid}>
            <div className={styles.copy}>
              <p className={styles.kicker}>OpenRecall</p>
              <h1>Find medicine recalls from official public sources.</h1>
              <p className={styles.lede}>
                Start with the live search app. The documentation is split into
                a short user guide for interpreting results and developer notes
                for maintaining the collector and adding countries.
              </p>
              <div className={styles.actions}>
                <a className="button button--primary button--lg" href="https://mrueda.github.io/openrecall/app/">
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

            <div className={styles.indexPanel} aria-label="OpenRecall country index preview">
              <a className={styles.identity} href="https://mrueda.github.io/openrecall/app/">
                <img className={styles.logo} src={logoUrl} alt="OpenRecall logo" />
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
            <h2 id="developer-heading">Maintain and extend OpenRecall.</h2>
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
