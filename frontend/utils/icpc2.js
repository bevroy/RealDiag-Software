// ICPC-2 line for a result: the codes when a reviewed mapping exists, else its
// status ("pending licensed mapping and review"). RealDiag does not generate
// ICPC-2 codes. Returns null when the response has no ICPC-2 fields.
//
// CommonJS so jest can load it without a Babel config (see __tests__).

function icpc2Label(result) {
  if (!result || (!result.icpc2 && !result.icpc2_status)) return null
  const codes = Array.isArray(result.icpc2) ? result.icpc2 : []
  return codes.length > 0 ? `ICPC-2: ${codes.join(', ')}` : `ICPC-2: ${result.icpc2_status}`
}

module.exports = { icpc2Label }
