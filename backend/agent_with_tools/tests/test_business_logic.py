#!/usr/bin/env python3
"""Test business logic estimator for the traffic case."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend tools to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_business_logic_estimator():
    """Test the business logic estimator for the specific traffic case."""
    
    try:
        from backend.agent_with_tools.tools.estimate_likelihood import estimate_business_likelihood
        
        # The actual traffic case from the user
        case_text = """Am 15. August 2025 gegen 14:30 Uhr fuhr ich auf der A1 Autobahn zwischen Basel und Bern in Richtung Bern. Ich war mit meinem BMW auf dem Weg zu einem wichtigen Geschäftstermin. Die Geschwindigkeitsbegrenzung auf diesem Abschnitt beträgt normalerweise 120 km/h, jedoch waren aufgrund von Bauarbeiten temporäre Schilder mit 80 km/h aufgestellt. Diese Schilder waren teilweise von Bäumen verdeckt und schlecht sichtbar. Ein mobiler Blitzer der Kantonspolizei Bern maß meine Geschwindigkeit mit 108 km/h. Nach Abzug der Toleranz von 5 km/h ergab sich eine Überschreitung von 23 km/h über dem temporären Limit von 80 km/h. Ich erhielt einen Strafbefehl über 600 CHF Busse plus 40 CHF Verfahrenskosten. Zusätzlich wurde mir der Führerausweis für 1 Monat entzogen. Ich bin der Meinung, dass die temporären Geschwindigkeitsbegrenzungen nicht ordnungsgemäß beschildert waren und die Messungen in einer unübersichtlichen Baustellen-Situation erfolgten. Außerdem war der Blitzer möglicherweise nicht korrekt geeicht - ich habe Zweifel an der Genauigkeit der Messung. Als Geschäftsmann bin ich auf meinen Führerausweis angewiesen. Kann ich erfolgreich Einspruch gegen den Strafbefehl und den Führerausweisentzug einlegen?"""
        
        category = "Strafverkehrsrecht"
        
        print("🧪 Testing Business Logic Estimator")
        print("=" * 50)
        print(f"📝 Category: {category}")
        print("📄 Case: Traffic speeding violation (23 km/h over limit)")
        print("-" * 50)
        
        result = estimate_business_likelihood(case_text, category)
        
        print("📊 Business Logic Results:")
        print(f"  Likelihood: {result['likelihood']}")
        print(f"  Raw Estimate: {result['raw_estimate']}")
        print(f"  Category Mapped: {result['category_mapped']}")
        print(f"  Subcategory: {result['subcategory']}")
        print(f"  Explanation: {result['explanation']}")
        
        # Test what the LLM should receive as context
        from backend.agent_with_tools.tools.estimate_likelihood import get_likelihood_explanation_context
        context = get_likelihood_explanation_context(result)
        print("\n🤖 LLM Context:")
        print(context)
        
        # Expected vs Actual
        expected_range = (10, 15)  # Based on user's observation
        actual = result['likelihood']
        
        if actual and expected_range[0] <= actual <= expected_range[1]:
            print(f"\n✅ Business logic is working correctly ({actual}% in expected range {expected_range})")
        else:
            print(f"\n❌ Business logic issue: got {actual}%, expected {expected_range[0]}-{expected_range[1]}%")
            
    except Exception as e:
        print(f"❌ Error testing business logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_business_logic_estimator()