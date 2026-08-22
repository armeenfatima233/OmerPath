export const BRAND = {
  name: "OmerPath",
  tagline: "Your Path. Your Future. Our Guidance.",
  student: {
    name: "Ali Raza",
    nationality: "Pakistan",
    degree: "BS Computer Science",
    gpa: "3.60 / 4.00",
    target: "Master's",
    ielts: "7.5",
    experience: "2 years",
  },
} as const;

export const PROTOTYPE_DATE = "Saturday, 15 August 2026";

export const ASSETS = {
  logo: "/manus-storage/omerpath-logo-160.webp",
  campus: "/manus-storage/omerpath-campus_0e75fd95.webp",
  publicHero: "/manus-storage/omerpath-public-hero_a8d8be6f.webp",
  publicOpportunities: "/manus-storage/omerpath-public-opportunities_531f89c2.webp",
  publicAi: "/manus-storage/omerpath-public-ai_a0c1b9ee.webp",
  publicPassport: "/manus-storage/omerpath-public-passport_46fb42f3.webp",
  publicFinal: "/manus-storage/omerpath-public-final_4bd0e465.webp",
  // Reuse the shipped editorial photography throughout the prototype so no route references missing assets.
  hero: "/manus-storage/omerpath-public-hero_a8d8be6f.webp",
  routeMap: "/manus-storage/omerpath-campus_0e75fd95.webp",
  passport: "/manus-storage/omerpath-public-passport_46fb42f3.webp",
  advisor: "/manus-storage/omerpath-public-ai_a0c1b9ee.webp",
  discovery: "/manus-storage/omerpath-public-opportunities_531f89c2.webp",
  application: "/manus-storage/omerpath-public-final_4bd0e465.webp",
  community: "/manus-storage/omerpath-campus_0e75fd95.webp",
  students: "/manus-storage/omerpath-public-opportunities_531f89c2.webp",
  studentDetail: "/manus-storage/omerpath-public-ai_a0c1b9ee.webp",
} as const;

export type Scholarship = {
  id: string;
  name: string;
  provider: string;
  country: string;
  degree: string;
  funding: "Fully Funded" | "Partially Funded";
  match: number | null;
  eligibilityStatus?: "eligible" | "ineligible" | "unknown" | null;
  deadline: string;
  deadlineNote: string;
  eligibility: string;
  fields: string[];
  sourceLabel: string;
  lastChecked: string;
  summary: string;
  fitReasons: string[];
  attention: string[];
  coverage: string[];
};

// Prototype/sample opportunity records. Dates and scores are intentionally labelled as sample UI data in the product.
export const SCHOLARSHIPS: Scholarship[] = [
  {
    id: "chevening",
    name: "Chevening Scholarships",
    provider: "UK Government",
    country: "United Kingdom",
    degree: "Master's",
    funding: "Fully Funded",
    match: 95,
    deadline: "03 Nov 2026",
    deadlineNote: "Confirm on the official website",
    eligibility: "Strong fit",
    fields: ["Computer Science", "Public Policy", "Business"],
    sourceLabel: "Official programme website",
    lastChecked: "15 Aug 2026",
    summary: "A UK government scholarship for future leaders, funding master's study with a focus on leadership potential and impact.",
    fitReasons: ["Nationality profile aligns", "Master's target aligns", "English test recorded", "Professional experience recorded"],
    attention: ["Recommendation letter still needed", "Leadership examples need strengthening"],
    coverage: ["Tuition", "Living allowance", "Travel", "Visa-related support"],
  },
  {
    id: "erasmus",
    name: "Erasmus Mundus Joint Masters",
    provider: "European Union",
    country: "Multiple Countries",
    degree: "Master's",
    funding: "Fully Funded",
    match: 91,
    deadline: "12 Jan 2027",
    deadlineNote: "Dates vary by programme",
    eligibility: "Strong fit",
    fields: ["Computer Science", "Data Science", "Engineering"],
    sourceLabel: "Official programme catalogue",
    lastChecked: "15 Aug 2026",
    summary: "A EU-funded joint master's delivered across multiple countries and partner universities.",
    fitReasons: ["Academic level aligns", "Relevant subject background", "English score recorded", "International mobility preference aligns"],
    attention: ["Programme-specific prerequisites must be checked"],
    coverage: ["Participation costs", "Travel contribution", "Living allowance"],
  },
  {
    id: "daad",
    name: "DAAD Development-Related Postgraduate Courses",
    provider: "DAAD",
    country: "Germany",
    degree: "Master's",
    funding: "Fully Funded",
    match: 89,
    deadline: "Varies by programme",
    deadlineNote: "Varies by participating course",
    eligibility: "Review programme",
    fields: ["Computer Science", "Engineering", "Development"],
    sourceLabel: "Official DAAD programme information",
    lastChecked: "15 Aug 2026",
    summary: "A postgraduate scholarship for students from developing countries, with eligibility and deadlines set by each participating course.",
    fitReasons: ["Degree target aligns", "Academic background can fit selected courses", "Experience profile can support application"],
    attention: ["Choose a qualifying course", "Confirm exact professional-experience requirement"],
    coverage: ["Monthly stipend", "Insurance", "Travel allowance where applicable"],
  },
  {
    id: "australia-awards",
    name: "Australia Awards Scholarships",
    provider: "Australian Government",
    country: "Australia",
    degree: "Master's",
    funding: "Fully Funded",
    match: 86,
    deadline: "30 Apr 2027",
    deadlineNote: "Eligibility differs by country",
    eligibility: "Check country rules",
    fields: ["Computer Science", "STEM", "Public Policy"],
    sourceLabel: "Official Australia Awards information",
    lastChecked: "15 Aug 2026",
    summary: "A fully funded Australian government scholarship for students from eligible countries pursuing postgraduate study.",
    fitReasons: ["Master's target aligns", "Academic profile is competitive", "Development-impact story can be relevant"],
    attention: ["Confirm Pakistan country intake", "Return-home conditions must be reviewed"],
    coverage: ["Tuition", "Living expenses", "Travel", "Health cover"],
  },
  {
    id: "fulbright",
    name: "Fulbright Foreign Student Program",
    provider: "Fulbright Program",
    country: "United States",
    degree: "Master's",
    funding: "Fully Funded",
    match: 84,
    deadline: "Country-specific",
    deadlineNote: "Set by local commission",
    eligibility: "Check local cycle",
    fields: ["Computer Science", "STEM", "Social Sciences"],
    sourceLabel: "Official Fulbright country programme",
    lastChecked: "15 Aug 2026",
    summary: "A U.S. government scholarship for international graduate study, with deadlines set by local country commissions.",
    fitReasons: ["Degree target aligns", "Academic record supports graduate study", "English score is recorded"],
    attention: ["Confirm local application window", "Prepare standardized-test plan if required"],
    coverage: ["Tuition support", "Living stipend", "Travel", "Health coverage"],
  },
  {
    id: "gates-cambridge",
    name: "Gates Cambridge Scholarship",
    provider: "University of Cambridge",
    country: "United Kingdom",
    degree: "Master's",
    funding: "Fully Funded",
    match: 79,
    deadline: "Course-dependent",
    deadlineNote: "Set by admissions deadline",
    eligibility: "Competitive reach",
    fields: ["Computer Science", "Engineering", "Research"],
    sourceLabel: "Official university scholarship page",
    lastChecked: "15 Aug 2026",
    summary: "A highly competitive scholarship for graduate study at the University of Cambridge.",
    fitReasons: ["Academic subject is supported", "Master's target aligns", "Profile demonstrates academic consistency"],
    attention: ["Admission competitiveness is very high", "Research/impact narrative needs stronger evidence"],
    coverage: ["University composition fee", "Maintenance allowance", "Selected additional support"],
  },
];

export const NAV_ITEMS = [
  { label: "Overview", href: "/dashboard", icon: "LayoutDashboard" },
  { label: "Scholarships", href: "/dashboard/scholarships", icon: "Compass" },
  { label: "Applications", href: "/dashboard/applications", icon: "ClipboardCheck" },
  { label: "Passport", href: "/dashboard/passport", icon: "BookOpenCheck" },
  { label: "AI Advisor", href: "/dashboard/advisor", icon: "Sparkles" },
];

export const SECONDARY_ITEMS = [
  { label: "Resources", href: "/dashboard/resources", icon: "Library" },
  { label: "Notifications", href: "/dashboard/notifications", icon: "Bell" },
  { label: "Profile", href: "/dashboard/profile", icon: "UserRound" },
  { label: "Settings", href: "/dashboard/settings", icon: "Settings2" },
];
