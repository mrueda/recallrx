import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    {
      type: 'doc',
      id: 'overview',
      label: 'Overview',
    },
    {
      type: 'category',
      label: 'For Users',
      items: [
        {
          type: 'doc',
          id: 'usage/quickstart',
          label: 'Use the App',
        },
        {
          type: 'doc',
          id: 'usage/safety-language',
          label: 'Safety Language',
        },
        {
          type: 'doc',
          id: 'usage/troubleshooting',
          label: 'Troubleshooting',
        },
      ],
    },
    {
      type: 'category',
      label: 'For Developers',
      items: [
        {
          type: 'doc',
          id: 'technical-details/architecture',
          label: 'Architecture',
        },
        {
          type: 'doc',
          id: 'technical-details/data-schema',
          label: 'Data Schema',
        },
        {
          type: 'doc',
          id: 'technical-details/source-adapters',
          label: 'Source Adapters',
        },
        {
          type: 'doc',
          id: 'technical-details/aemps-collector',
          label: 'AEMPS Collector',
        },
        {
          type: 'doc',
          id: 'reference/cli',
          label: 'CLI',
        },
        {
          type: 'doc',
          id: 'usage/operations',
          label: 'Operations',
        },
      ],
    },
    {
      type: 'category',
      label: 'About',
      items: [
        {
          type: 'doc',
          id: 'about/roadmap',
          label: 'Roadmap',
        },
        {
          type: 'doc',
          id: 'about/license',
          label: 'License',
        },
      ],
    },
  ],
};

export default sidebars;
