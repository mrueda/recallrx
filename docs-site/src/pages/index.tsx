import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

const userLinks = [
  {
    label: 'Search',
    title: 'Search medicine recalls',
    text: 'Choose a country and search by medicine name, product code, lot, alert number, year, or date.',
    url: 'https://mrueda.github.io/recallrx/app/',
  },
  {
    label: 'Understand',
    title: 'Understand a result',
    text: 'See what the dates, coloured labels, update status, and official source links mean.',
    url: '/recallrx/docs/usage/quickstart',
  },
  {
    label: 'Safety',
    title: 'Know the limits',
    text: 'Learn why a search result is a starting point and when to check the original notice or ask a professional.',
    url: '/recallrx/docs/usage/safety-language',
  },
];

const developerLinks = [
  {
    label: 'Architecture',
    title: 'How RecallRx is built',
    text: 'Follow the path from an official notice to the daily data files and the public search app.',
    url: '/recallrx/docs/technical-details/architecture',
  },
  {
    label: 'Data',
    title: 'Data files and fields',
    text: 'See the common JSON format used for notices from each country.',
    url: '/recallrx/docs/technical-details/data-schema',
  },
  {
    label: 'Extend',
    title: 'Add another country',
    text: 'Build and test a collector for another medicines authority.',
    url: '/recallrx/docs/technical-details/source-adapters',
  },
];

const rows = [
  ['Country', 'Authority'],
  ['Spain', 'AEMPS'],
  ['Portugal', 'INFARMED'],
  ['France', 'ANSM'],
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
              <h1>Find medicine recall notices from official sources.</h1>
              <p className={styles.lede}>
                RecallRx brings together public recall notices from medicines
                authorities in Spain, Portugal, and France. It updates each day
                and links every result to the original source.
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
                <span>Available countries</span>
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
                <span className={styles.source}>official notices</span>
                <span className={styles.static}>daily updates</span>
                <span className={styles.safe}>source links</span>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.sections} id="user-docs" aria-labelledby="user-heading">
          <div className={styles.sectionHeader}>
            <p>User docs</p>
            <h2 id="user-heading">Help with searching and reading results.</h2>
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
            <h2 id="developer-heading">For maintainers and contributors.</h2>
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
