import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

const featureLinks = [
  {
    label: 'Setup',
    title: 'Build the dataset',
    text: 'Run the Python collector, validate JSON output, and create the static deploy directory.',
    to: '/docs/usage/quickstart',
  },
  {
    label: 'Operations',
    title: 'Run daily updates',
    text: 'Use GitHub Actions to collect AEMPS recalls, validate changes, and keep the Pages dataset current.',
    to: '/docs/usage/operations',
  },
  {
    label: 'Schema',
    title: 'Understand records',
    text: 'Read the country-aware recall model, product code systems, confidence, and warning fields.',
    to: '/docs/technical-details/data-schema',
  },
  {
    label: 'Expansion',
    title: 'Add countries',
    text: 'Implement source adapters for new authorities without changing the static frontend contract.',
    to: '/docs/technical-details/source-adapters',
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
              <h1>Searchable medicine recalls from official public sources.</h1>
              <p className={styles.lede}>
                OpenRecall turns AEMPS recall pages and PDFs into a static
                JSON dataset and browser search app. The first adapter targets
                Spain, while the schema is designed for future country sources.
              </p>
              <div className={styles.actions}>
                <Link className="button button--primary button--lg" to="/app">
                  Open live search
                </Link>
                <Link className="button button--primary button--lg" to="/docs/overview">
                  Read the docs
                </Link>
                <Link className="button button--secondary button--lg" to="/docs/usage/quickstart">
                  Quick start
                </Link>
                <Link className="button button--secondary button--lg" to="/docs/technical-details/data-schema">
                  Data schema
                </Link>
              </div>
            </div>

            <div className={styles.indexPanel} aria-label="OpenRecall country index preview">
              <Link className={styles.identity} to="/docs/overview">
                <img className={styles.logo} src={logoUrl} alt="OpenRecall logo" />
                <span>OpenRecall index</span>
              </Link>
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

        <section className={styles.sections}>
          <div className={styles.grid}>
            {featureLinks.map((feature) => (
              <Link className={styles.card} to={feature.to} key={feature.title}>
                <span>{feature.label}</span>
                <h2>{feature.title}</h2>
                <p>{feature.text}</p>
              </Link>
            ))}
          </div>
        </section>
      </main>
    </Layout>
  );
}
