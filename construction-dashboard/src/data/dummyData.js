export const reportMeta = {
  year: 2025,
  week: 17,
  reportDate: '2025년 4월 23일(수)',
};

export const sites = [
  { id: 'A', name: 'A현장', location: '서울 강남구', type: '공동주택', manager: '김현장' },
  { id: 'B', name: 'B현장', location: '경기 성남시', type: '오피스빌딩', manager: '이현장' },
  { id: 'C', name: 'C현장', location: '인천 연수구', type: '물류센터', manager: '박현장' },
];

export const progressData = {
  A: {
    planned: 68.5,
    actual: 65.2,
    weeklyPlanned: 2.5,
    weeklyActual: 2.1,
    status: 'warning',
    milestone: '골조공사 3층',
    nextMilestone: '골조공사 5층 완료',
    trend: [
      { week: '13주', planned: 55.0, actual: 54.5 },
      { week: '14주', planned: 58.5, actual: 57.8 },
      { week: '15주', planned: 62.0, actual: 60.9 },
      { week: '16주', planned: 65.5, actual: 63.2 },
      { week: '17주', planned: 68.5, actual: 65.2 },
    ],
  },
  B: {
    planned: 42.0,
    actual: 43.5,
    weeklyPlanned: 3.0,
    weeklyActual: 3.2,
    status: 'good',
    milestone: '기초공사 완료',
    nextMilestone: '지하 2층 골조 완료',
    trend: [
      { week: '13주', planned: 29.0, actual: 30.1 },
      { week: '14주', planned: 32.5, actual: 33.9 },
      { week: '15주', planned: 36.0, actual: 37.8 },
      { week: '16주', planned: 39.5, actual: 40.3 },
      { week: '17주', planned: 42.0, actual: 43.5 },
    ],
  },
  C: {
    planned: 81.0,
    actual: 74.5,
    weeklyPlanned: 4.0,
    weeklyActual: 2.5,
    status: 'danger',
    milestone: '외장공사 진행 중',
    nextMilestone: '준공 D-45일',
    trend: [
      { week: '13주', planned: 68.0, actual: 64.5 },
      { week: '14주', planned: 71.5, actual: 67.2 },
      { week: '15주', planned: 74.5, actual: 70.0 },
      { week: '16주', planned: 77.5, actual: 72.1 },
      { week: '17주', planned: 81.0, actual: 74.5 },
    ],
  },
};

export const costData = {
  A: {
    budget: 85_000_000_000,
    executed: 55_250_000_000,
    rate: 65.0,
    plannedRate: 63.5,
    forecast: 86_200_000_000,
    overBudget: true,
    overAmount: 1_200_000_000,
    monthly: [
      { month: '12월', planned: 38.0, actual: 37.2 },
      { month: '1월', planned: 45.5, actual: 44.8 },
      { month: '2월', planned: 53.0, actual: 52.1 },
      { month: '3월', planned: 59.0, actual: 58.5 },
      { month: '4월', planned: 63.5, actual: 65.0 },
    ],
  },
  B: {
    budget: 120_000_000_000,
    executed: 43_200_000_000,
    rate: 36.0,
    plannedRate: 37.5,
    forecast: 118_500_000_000,
    overBudget: false,
    overAmount: 0,
    monthly: [
      { month: '12월', planned: 18.0, actual: 17.5 },
      { month: '1월', planned: 23.5, actual: 22.8 },
      { month: '2월', planned: 28.0, actual: 27.1 },
      { month: '3월', planned: 32.0, actual: 31.8 },
      { month: '4월', planned: 37.5, actual: 36.0 },
    ],
  },
  C: {
    budget: 55_000_000_000,
    executed: 48_950_000_000,
    rate: 89.0,
    plannedRate: 84.0,
    forecast: 57_300_000_000,
    overBudget: true,
    overAmount: 2_300_000_000,
    monthly: [
      { month: '12월', planned: 65.0, actual: 68.2 },
      { month: '1월', planned: 72.0, actual: 74.5 },
      { month: '2월', planned: 77.5, actual: 80.1 },
      { month: '3월', planned: 81.0, actual: 85.2 },
      { month: '4월', planned: 84.0, actual: 89.0 },
    ],
  },
};

export const safetyData = {
  A: {
    noAccidentDays: 142,
    inspectionRate: 95,
    pendingActions: 3,
    nearMiss: 1,
    inspections: [
      { category: '추락방지', completed: true },
      { category: '전기안전', completed: true },
      { category: '화재예방', completed: true },
      { category: '중장비 안전', completed: false },
      { category: '개인보호구', completed: true },
    ],
    riskLevel: 'low',
  },
  B: {
    noAccidentDays: 89,
    inspectionRate: 88,
    pendingActions: 7,
    nearMiss: 2,
    inspections: [
      { category: '추락방지', completed: true },
      { category: '전기안전', completed: false },
      { category: '화재예방', completed: true },
      { category: '중장비 안전', completed: true },
      { category: '개인보호구', completed: false },
    ],
    riskLevel: 'medium',
  },
  C: {
    noAccidentDays: 34,
    inspectionRate: 72,
    pendingActions: 12,
    nearMiss: 4,
    inspections: [
      { category: '추락방지', completed: false },
      { category: '전기안전', completed: true },
      { category: '화재예방', completed: false },
      { category: '중장비 안전', completed: false },
      { category: '개인보호구', completed: true },
    ],
    riskLevel: 'high',
  },
};

export const formatBillion = (num) => {
  const billion = num / 100_000_000;
  return `${billion.toLocaleString('ko-KR', { maximumFractionDigits: 1 })}억`;
};
