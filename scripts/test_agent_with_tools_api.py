#!/usr/bin/env python3
"""
Test script for the FastAPI agent endpoint.
"""

import requests
import time

# Test cases focusing on the 2 categories supported by the classifier
test_cases = [
    {
        "name": "Employment Law - Wrongful Termination (Arbeitsrecht)",
        "data": {
            "text": "Ich bin 45 Jahre alt und arbeite seit 8 Jahren als Projektmanager bei einer Schweizer IT-Firma in Zürich. Letzte Woche wurde mir vom Geschäftsführer mitgeteilt, dass mein Arbeitsvertrag mit sofortiger Wirkung gekündigt wird, angeblich wegen 'mangelnder Leistung'. Ich erhielt keine schriftliche Kündigung und keine Kündigungsfrist wurde eingehalten. In den letzten 2 Jahren habe ich drei große Projekte erfolgreich abgeschlossen und erhielt sogar eine Leistungsprämie von 5000 CHF im Januar 2025. Es gab nie Abmahnungen, Verwarnungen oder negative Leistungsbeurteilungen. Mein Verdacht ist, dass die Kündigung erfolgte, weil ich vor 3 Monaten eine Beschwerde bei der HR-Abteilung über Mobbing durch meinen direkten Vorgesetzten eingereicht habe. Dieser hatte mich wiederholt vor Kollegen bloßgestellt und mir wichtige Informationen vorenthalten. Mein Arbeitsvertrag sieht eine 3-monatige Kündigungsfrist vor. Ich verdiene 95.000 CHF brutto jährlich plus Bonuszahlungen. Kann ich gegen diese fristlose Kündigung rechtlich vorgehen und Schadenersatz fordern?",
            "metadata": {
                "language": "de",
                "court_level": "district",
                "preferred_units": "months"
            }
        }
    },
    {
        "name": "Employment Law - Wage Dispute (Arbeitsrecht)",
        "data": {
            "text": "I have been working as a senior software developer for a fintech startup in Geneva for 18 months. My employment contract states a gross annual salary of 120,000 CHF, payable in 13 monthly installments (including 13th month salary). However, for the past 4 months, I have only received partial payments - approximately 60-70% of my monthly salary of 9,230 CHF. My employer claims the company is experiencing 'temporary cash flow issues' and promises to pay the outstanding amounts 'soon'. The total amount owed to me is now approximately 15,000 CHF. I have documented proof of all missing payments and have sent multiple written requests to HR and management. My employment contract contains no clauses allowing for reduced payments during financial difficulties. Additionally, I have been working significant overtime (10-15 hours per week extra) for which I should receive compensation, but this has also not been paid. I am concerned about the company's financial stability and whether I should continue working there. Last week, two other colleagues left due to similar payment issues. Can I take legal action to recover my unpaid wages and overtime compensation? Am I entitled to terminate my contract immediately due to non-payment of salary?",
            "metadata": {
                "language": "en",
                "court_level": "cantonal",
                "preferred_units": "months"
            }
        }
    },
    {
        "name": "Traffic Law - Speeding Violation (Strafverkehrsrecht)",
        "data": {
            "text": "Am 15. August 2025 gegen 14:30 Uhr fuhr ich auf der A1 Autobahn zwischen Basel und Bern in Richtung Bern. Ich war mit meinem BMW auf dem Weg zu einem wichtigen Geschäftstermin. Die Geschwindigkeitsbegrenzung auf diesem Abschnitt beträgt normalerweise 120 km/h, jedoch waren aufgrund von Bauarbeiten temporäre Schilder mit 80 km/h aufgestellt. Diese Schilder waren teilweise von Bäumen verdeckt und schlecht sichtbar. Ein mobiler Blitzer der Kantonspolizei Bern maß meine Geschwindigkeit mit 108 km/h. Nach Abzug der Toleranz von 5 km/h ergab sich eine Überschreitung von 23 km/h über dem temporären Limit von 80 km/h. Ich erhielt einen Strafbefehl über 600 CHF Busse plus 40 CHF Verfahrenskosten. Zusätzlich wurde mir der Führerausweis für 1 Monat entzogen. Ich bin der Meinung, dass die temporären Geschwindigkeitsbegrenzungen nicht ordnungsgemäß beschildert waren und die Messungen in einer unübersichtlichen Baustellen-Situation erfolgten. Außerdem war der Blitzer möglicherweise nicht korrekt geeicht - ich habe Zweifel an der Genauigkeit der Messung. Als Geschäftsmann bin ich auf meinen Führerausweis angewiesen. Kann ich erfolgreich Einspruch gegen den Strafbefehl und den Führerausweisentzug einlegen?",
            "metadata": {
                "language": "de", 
                "court_level": "district",
                "preferred_units": "weeks"
            }
        }
    },
    {
        "name": "Traffic Law - DUI Case (Strafverkehrsrecht)",
        "data": {
            "text": "On the evening of September 20, 2025, I attended a business dinner in downtown Zurich. I had consumed approximately 2 glasses of wine over a 3-hour period (from 18:00 to 21:00) along with a full meal. I felt completely sober and capable of driving. At around 21:30, I was driving my company car (Audi A4) home to my apartment in Winterthur when I was stopped at a routine traffic control checkpoint near the Zurich main train station. The police officer asked me to perform a breathalyzer test, which showed a reading of 0.6 promille (0.06% BAC). Under Swiss law, the legal limit is 0.5 promille, so I was over the limit by 0.1 promille. I was immediately issued a fine of 1,200 CHF and my license was suspended for 3 months. Additionally, I must attend a mandatory driving course costing 800 CHF. I am a sales manager and travel frequently for work - losing my driving license for 3 months would severely impact my ability to perform my job and could result in termination of my employment. I believe the breathalyzer device may not have been properly calibrated, and I question whether the small amount over the limit justifies such severe penalties. I have a clean driving record with no previous violations in 15 years of driving. Is there a possibility to challenge this penalty and reduce the license suspension period, particularly given the minimal nature of the violation and my professional circumstances?",
            "metadata": {
                "language": "en",
                "court_level": "cantonal",
                "preferred_units": "months"
            }
        }
    },
    {
        "name": "Unsupported Category - Family Law (Should become Andere)",
        "data": {
            "text": "I am going through a difficult divorce from my husband of 12 years here in Switzerland. We have two children aged 8 and 10. My husband is a Swiss citizen and I am originally from Germany but have been living in Switzerland for 15 years and have a C permit. We own a house together in Lausanne worth approximately 800,000 CHF with a remaining mortgage of 300,000 CHF. We also have joint savings of about 150,000 CHF and he has a significant pension fund from his job at a major bank. My husband has been emotionally abusive and has threatened to take the children away from me and move back to his parents' house. He earns significantly more than I do (he makes 180,000 CHF per year as a bank manager, while I work part-time as a translator earning about 45,000 CHF annually). I am concerned about child custody arrangements, division of our assets, and whether I will receive adequate spousal support. He has also hidden some financial assets and transferred money to accounts I don't have access to. I need legal representation but am worried about the costs and how long the divorce proceedings might take. What are my rights as a foreign spouse, and how can I protect my interests and those of my children during this divorce?",
            "metadata": {
                "language": "en",
                "court_level": "cantonal",
                "preferred_units": "months"
            }
        }
    }
]

def test_agent_endpoint(base_url="http://localhost:8000"):
    """Test the agent endpoint with various cases."""
    
    print("🧪 Testing Legal Agent FastAPI Endpoint")
    print("=" * 50)
    print("📋 Test Cases Overview:")
    print("  1. Employment Law - Wrongful Termination (should classify as Arbeitsrecht)")
    print("  2. Employment Law - Wage Dispute (should classify as Arbeitsrecht)") 
    print("  3. Traffic Law - Speeding Violation (should classify as Strafverkehrsrecht)")
    print("  4. Traffic Law - DUI Case (should classify as Strafverkehrsrecht)")
    print("  5. Family Law - Divorce Case (should classify as Andere - unsupported)")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Make request to the agent endpoint
            response = requests.post(
                f"{base_url}/api/agent_with_tools",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=90  # Allow up to 90 seconds for complete legal analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Category: {result.get('category', 'N/A')}")
                print(f"Win Likelihood: {result.get('likelihood_win', 'N/A')}")
                print(f"Estimated Time: {result.get('estimated_time', 'N/A')}")
                print(f"Estimated Cost: {result.get('estimated_cost', 'N/A')}")
                
                if result.get('explanation'):
                    print(f"Explanation: {result['explanation'][:200]}...")
                
            else:
                print(f"❌ Failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out (took more than 90 seconds)")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - is the server running?")
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")
        
        # Wait a bit between requests
        if i < len(test_cases):
            print("\nWaiting 2 seconds before next test...")
            time.sleep(2)

def test_basic_endpoints(base_url="http://localhost:8000"):
    """Test basic API endpoints."""
    print("\n🔍 Testing Basic Endpoints")
    print("-" * 30)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test API root
    try:
        response = requests.get(f"{base_url}/api/")
        if response.status_code == 200:
            print("✅ API root working")
        else:
            print(f"❌ API root failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API root error: {e}")

if __name__ == "__main__":
    print("Starting API endpoint tests...\n")
    
    # Test basic endpoints first
    test_basic_endpoints()
    
    # Test the agent endpoint
    test_agent_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")