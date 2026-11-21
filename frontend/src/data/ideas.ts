import type { KpiCard, CoverItem } from './overview';

export interface IdeaMetadata {
  id: number;
  title: string;
  shortTitle: string;
  icon: string;
  domain: string;
  rank: number;
  compositeScore: number;
  novelty: number;
  feasibility: number;
  q1pub: number;
  phdImpact: number;
  risk: number;
  complexity: number;
  targetVenue: string;
  status: 'Recommended';
  docType: string;
  subtitle: string;
  coverItems: CoverItem[];
  kpis: KpiCard[];
}

export const ideaMetadata: IdeaMetadata[] = [
  {
    id: 1,
    title: 'The Boundaries of Evidence-Grounded Trust in Multi-Agent Scientific Debate, with a Controlled Benchmark for Sycophantic Consensus',
    shortTitle: 'The Trust Boundary',
    icon: '🤖',
    domain: 'Agentic AI / Reasoning',
    rank: 1,
    compositeScore: 4.6,
    novelty: 5, feasibility: 5, q1pub: 5, phdImpact: 5, risk: 4, complexity: 4,
    targetVenue: 'TACL (rolling) · EMNLP 2028 fallback',
    status: 'Recommended',
    docType: 'FYDP Proposal · Idea 1 of 1 · Rank #1 · P0 gate 13/13',
    subtitle: 'Domain: Agentic AI · LLM Reasoning · Multi-Agent Systems · Trust Calibration · P0 status · Core row 2/24 (GPQA-Main seed 1) complete: feasibility + timing, efficacy n.s. (McNemar p=0.086)',
    coverItems: [
      { label: 'Target Venue', value: 'TACL (rolling) · EMNLP 2028 fallback' },
      { label: 'P0 Gate', value: '13 / 13 passed' },
      { label: 'P0 Tests', value: '514' },
      { label: 'Project Report', value: '70-pp report · 19-pp journal · 0 undefined refs' },
      { label: 'Core Matrix', value: 'Row 2/24 complete · 798 debates · p=0.086 (n.s.)' },
    ],
    kpis: [
      { value: '514', label: 'P0 Tests Passing', variant: 'default' },
      { value: '13/13', label: 'P0 Gate Passed', variant: 'green' },
      { value: '24', label: 'Core Runs', variant: 'sky' },
      { value: '300', label: 'Benchmark Target (180 floor)', variant: 'amber' },
      { value: '3', label: 'Agent Roles in Pipeline', variant: 'rose' },
    ],
  },
];
