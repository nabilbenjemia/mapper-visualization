//TODO: remove this
export const sources = [
    { key: "2026-03-18T14-34-36Z_europe-germany_b9dada", label: "Germany (Gaussian)", region: "germany" },
    { key: "2026-06-30T05-14-58Z_europe-germany_e046f3", label: "Germany (Uniform)", region: "germany" },
    { key: "2026-03-05T15-27-24Z_germany-saarland_aea13a", label: "Saarland (Gaussian)", region: "saarland" },
    { key: "2026-08-16T20-17-33Z_africa_v3_recovered", label: "Africa (Exponential)", region: "africa" },
]

const AFRICA = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon",
    "Central African Republic", "Chad", "Democratic Republic of the Congo", "Djibouti",
    "Egypt", "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana",
    "Guinea", "Guinea Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
    "Madagascar", "Malawi", "Mali", "Mauritania", "Morocco", "Mozambique", "Namibia",
    "Niger", "Nigeria", "Republic of the Congo", "Rwanda", "Senegal", "Sierra Leone",
    "Somalia", "Somaliland", "South Africa", "South Sudan", "Sudan", "Swaziland", "Togo",
    "Tunisia", "Uganda", "United Republic of Tanzania", "Western Sahara", "Zambia",
    "Zimbabwe",
]

export const regionCountries = {
    germany: ["Germany"],
    saarland: ["Germany"],
    africa: AFRICA,
}
