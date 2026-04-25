def billing_suggestions(customer_name: str, amount: float, currency: str) -> dict:
    return {
        'summary': f'Invoice {customer_name} for {amount:.2f} {currency}',
        'recommended_terms': 'Net 7 days for new customers, Net 15 for repeat customers',
        'follow_up': 'Send reminder 3 days before due date and 2 days after due date if unpaid',
    }
