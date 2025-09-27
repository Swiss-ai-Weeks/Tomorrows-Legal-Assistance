#!/usr/bin/env python3
"""Test the improved traffic case analysis."""

import requests

def test_traffic_case_improved():
    """Test the traffic case with improved baseline constraints."""
    
    case_input = {
        "text": """Am 15. August 2025 gegen 14:30 Uhr fuhr ich auf der A1 Autobahn zwischen Basel und Bern in Richtung Bern. Ich war mit meinem BMW auf dem Weg zu einem wichtigen Geschäftstermin. Die Geschwindigkeitsbegrenzung auf diesem Abschnitt beträgt normalerweise 120 km/h, jedoch waren aufgrund von Bauarbeiten temporäre Schilder mit 80 km/h aufgestellt. Diese Schilder waren teilweise von Bäumen verdeckt und schlecht sichtbar. Ein mobiler Blitzer der Kantonspolizei Bern maß meine Geschwindigkeit mit 108 km/h. Nach Abzug der Toleranz von 5 km/h ergab sich eine Überschreitung von 23 km/h über dem temporären Limit von 80 km/h. Ich erhielt einen Strafbefehl über 600 CHF Busse plus 40 CHF Verfahrenskosten. Zusätzlich wurde mir der Führerausweis für 1 Monat entzogen. Ich bin der Meinung, dass die temporären Geschwindigkeitsbegrenzungen nicht ordnungsgemäß beschildert waren und die Messungen in einer unübersichtlichen Baustellen-Situation erfolgten. Außerdem war der Blitzer möglicherweise nicht korrekt geeicht - ich habe Zweifel an der Genauigkeit der Messung. Als Geschäftsmann bin ich auf meinen Führerausweis angewiesen. Kann ich erfolgreich Einspruch gegen den Strafbefehl und den Führerausweisentzug einlegen?""",
        "metadata": {
            "language": "de",
            "court_level": "district",
            "preferred_units": "weeks"
        }
    }
    
    print("🧪 Testing Improved Traffic Case Analysis")
    print("=" * 50)
    print("📝 Expected Business Logic Baseline: 12% (10-15% range)")
    print("📏 Expected Final Score Range: 1-32% (baseline ±20%)")
    print("🎯 Previous Problematic Score: 60% (way too high)")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/agent_with_tools",
            json=case_input,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            category = result.get('category', 'Unknown')
            likelihood = result.get('likelihood_win', 'N/A')
            explanation = result.get('explanation', '')
            source_docs = result.get('source_documents', [])
            
            print("✅ Backend Response:")
            print(f"  Category: {category}")
            print(f"  Likelihood: {likelihood}")
            print(f"  Time: {result.get('estimated_time', 'N/A')}")
            print(f"  Cost: {result.get('estimated_cost', 'N/A')}")
            
            # Analyze if improvements worked
            if likelihood and likelihood != 'N/A':
                likelihood_num = int(likelihood.replace('%', '')) if isinstance(likelihood, str) else likelihood
                
                print("\n📊 Analysis:")
                print("  Business Logic Baseline: 12%")
                print(f"  Final Score: {likelihood_num}%")
                print(f"  Deviation: {likelihood_num - 12:+d} percentage points")
                
                if 1 <= likelihood_num <= 32:  # Within ±20% of 12%
                    print("✅ IMPROVEMENT SUCCESS: Score within expected range!")
                    if 8 <= likelihood_num <= 16:  # Very close to baseline
                        print("🎉 EXCELLENT: Score very close to business logic baseline!")
                elif likelihood_num <= 40:
                    print("✅ GOOD: Significant improvement, much closer to baseline")
                else:
                    print("❌ STILL TOO HIGH: Score still deviating too much from baseline")
            
            # Check source documents
            print(f"\n📚 Source Documents ({len(source_docs)}):")
            traffic_docs = 0
            for doc in source_docs:
                title = doc.get('title', 'Unknown')
                if any(pattern in title for pattern in ['SR-741', 'SR-742', 'Traffic', 'Road']):
                    print(f"  ✅ {title} (TRAFFIC LAW)")
                    traffic_docs += 1
                elif 'fallback' in doc.get('id', ''):
                    print(f"  📚 {title} (FALLBACK)")
                    traffic_docs += 1
                else:
                    print(f"  ❌ {title} (IRRELEVANT)")
            
            if traffic_docs > 0:
                print(f"✅ Document Retrieval: {traffic_docs}/{len(source_docs)} relevant")
            else:
                print("❌ Document Retrieval: Still getting irrelevant documents")
            
            # Check explanation consistency
            if 'business logic' in explanation.lower():
                print("✅ Explanation mentions business logic baseline")
            else:
                print("⚠️ Explanation doesn't mention business logic")
            
            print("\n📝 Explanation Preview:")
            print(f"  {explanation[:200]}...")
            
        else:
            print(f"❌ Backend Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_traffic_case_improved()