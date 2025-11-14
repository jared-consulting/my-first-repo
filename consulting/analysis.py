from typing import Dict, Any, List


def build_summary(data: Dict[str, Any]) -> str:
    challenges: List[str] = data.get("challenges", []) or []
    ch_text = "; ".join(challenges) if challenges else "None provided"
    employees = data.get("employees")
    employees_text = str(employees) if employees is not None else "(unspecified)"
    revenue = data.get("annual_revenue")
    revenue_text = f"${revenue:,.2f}" if isinstance(revenue, (int, float)) else "(unspecified)"
    return (
        "\n=== Business Summary ===\n"
        f"Name: {data.get('business_name', '(Unnamed)')}\n"
        f"Industry: {data.get('industry', '(unspecified)')}\n"
        f"Employees: {employees_text}\n"
        f"Annual Revenue: {revenue_text}\n"
        f"Main Challenges: {ch_text}\n"
    )
