export const formatCurrency = (value, currency = 'EUR') => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: currency,
  }).format(value)
}

export const formatPercent = (value) => {
  const sign = value >= 0 ? '+' : ''
  return sign + value.toFixed(2) + '%'
}

export const formatNumber = (value, decimals = 2) => {
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export const getColorClass = (value) => {
  if (value > 0) return 'text-green-600'
  if (value < 0) return 'text-red-600'
  return 'text-gray-600'
}

export const getBackgroundColorClass = (value) => {
  if (value > 0) return 'bg-green-50'
  if (value < 0) return 'bg-red-50'
  return 'bg-gray-50'
}
