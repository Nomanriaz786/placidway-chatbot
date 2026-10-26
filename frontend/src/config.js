export const QUOTE_URL = 'https://www.placidway.com/request-info'
export const HISTORY_LIMIT = 10

export const DISCLAIMER =
  'For information only, not medical advice. Please consult a qualified doctor about your situation.'

// The only pages the assistant answers from (mirrors backend/chatbot/sources.py).
export const SOURCES = [
  { url: 'https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center', title: 'ITC Immunity Therapy Center', kind: 'Clinic profile' },
  { url: 'https://www.placidway.com/package/7903/Alternative-Adenocarcinoma-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC', title: 'Adenocarcinoma cancer treatment', kind: 'Package' },
  { url: 'https://www.placidway.com/package/7902/Alternative-Adrenal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC', title: 'Adrenal cancer treatment', kind: 'Package' },
  { url: 'https://www.placidway.com/package/7901/Alternative-Anal-Cancer-Treatment-Package-in-Tijuana-Mexico-by-ITC', title: 'Anal cancer treatment', kind: 'Package' },
  { url: 'https://www.placidway.com/profile-videos/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center', title: 'ITC clinic videos', kind: 'Videos' },
  { url: 'https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center', title: 'ITC price list', kind: 'Price list' },
  { url: 'https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1', title: 'Alternative medicine prices abroad', kind: 'Price comparison' },
]

export const SUGGESTIONS = [
  'How much does adenocarcinoma treatment cost in Tijuana?',
  'What is included in the anal cancer treatment package?',
  'What does ITC charge for breast cancer treatment?',
  '¿Cuánto cuesta el programa ambulatorio?',
]

export function sourceFor(url) {
  return SOURCES.find((s) => s.url === url) ?? { url, title: url, kind: 'Page' }
}
