from text_normalizer import normalize_property_name


properties = [
    "customer_retention_rate",
    "Customer Retention Rate",
    "number_of_employees",
    "number of employees",
    "Revenue"
]


for property_name in properties:

    normalized = normalize_property_name(property_name)

    print(property_name)
    print("  →", normalized)