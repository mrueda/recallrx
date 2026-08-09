import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    {
      type: 'doc',
      id: 'overview',
      label: 'Start Here',
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
          label: 'Limits and Safety',
        },
        {
          type: 'doc',
          id: 'usage/troubleshooting',
          label: 'Help with the App',
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
          label: 'Data Format',
        },
        {
          type: 'doc',
          id: 'technical-details/source-adapters',
          label: 'Country Collectors',
        },
        {
          type: 'doc',
          id: 'technical-details/aemps-collector',
          label: 'Spain (AEMPS)',
        },
        {
          type: 'doc',
          id: 'reference/cli',
          label: 'Command Line',
        },
        {
          type: 'doc',
          id: 'usage/operations',
          label: 'Updates and Deployment',
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
