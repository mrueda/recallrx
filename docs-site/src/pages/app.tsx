import Layout from '@theme/Layout';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './app.module.css';

export default function AppPage() {
  const searchUrl = useBaseUrl('/search/index.html');

  return (
    <Layout
      title="Live Search"
      description="OpenRecall live static recall search app">
      <main className={styles.page}>
        <header className={styles.header}>
          <div>
            <p className={styles.kicker}>OpenRecall</p>
            <h1>Live recall search</h1>
            <p>
              Static HTML app backed by the generated country-aware JSON dataset.
            </p>
          </div>
          <a className="button button--secondary" href={searchUrl} target="_blank" rel="noreferrer">
            Open full page
          </a>
        </header>
        <section className={styles.frameShell} aria-label="OpenRecall live search app">
          <iframe
            className={styles.frame}
            src={searchUrl}
            title="OpenRecall live recall search"
          />
        </section>
      </main>
    </Layout>
  );
}
