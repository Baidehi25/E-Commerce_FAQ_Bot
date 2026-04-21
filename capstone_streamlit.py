import streamlit as st
import os, re
from datetime import datetime, timedelta
from typing import TypedDict, List

st.set_page_config(page_title="ShopEasy Support", page_icon="ShopEasy", layout="wide")

@st.cache_resource
def load_agent():
    from langchain_groq import ChatGroq
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    import chromadb
    from sentence_transformers import SentenceTransformer

    os.environ["GROQ_API_KEY"]="YOUR_GROQ_API_KEY"

    llm=ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    embedder=SentenceTransformer("all-MiniLM-L6-v2")

    docs=[
        {
            "id": "doc_001",
            "topic": "Return & Refund Policy",
            "text": 'ShopEasy offers a 30-day return policy on all eligible products from the date of delivery. To qualify for a return, items must be unused, in their original packaging, and accompanied by proof of purchase such as an order confirmation email or invoice. Products in the following categories are non-returnable for hygiene and safety reasons: innerwear, swimwear, earrings, and opened personal care products. To initiate a return, customers must log in to their ShopEasy account, navigate to My Orders, select the item they wish to return, and click Request Return. A return pickup will be scheduled within 2 business days of approval. Customers can also drop off items at any ShopEasy partner courier centre. Refunds are processed within 5 to 7 business days after the returned item is received and inspected at our warehouse. Refunds are credited to the original payment method credit card, debit card, UPI, or ShopEasy Wallet. If you paid via Cash on Delivery, the refund will be added to your ShopEasy Wallet or transferred to your bank account upon request. Shipping charges are non-refundable unless the return is due to a defective or incorrect item sent by ShopEasy. Exchanges are allowed for size or colour variants of the same product, subject to availability. If the requested variant is unavailable, a full refund will be issued instead.'
        },
        {
            "id": "doc_002",
            "topic": "Shipping & Delivery",
            "text": 'ShopEasy delivers across India to over 27,000 pin codes. Standard delivery takes 4 to 6 business days from the date of order confirmation. Express delivery, available in select metro cities including Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Pune, and Kolkata, guarantees delivery within 1 to 2 business days for an additional fee of Rs.99 per order. Free shipping is available on all orders above Rs.499. Orders below Rs.499 attract a standard shipping charge of Rs.49. Express delivery charges are in addition to the standard shipping fee. Once an order is shipped, customers receive a tracking link via SMS and email. Orders can also be tracked from the My Orders section in the ShopEasy app or website. ShopEasy partners with courier services including BlueDart, Delhivery, Ekart, and DTDC depending on the delivery pin code. If a delivery attempt fails due to the customer being unavailable, two more attempts will be made on subsequent business days. After three failed attempts, the order is returned to the warehouse and a refund is issued minus the shipping charge. For remote or difficult-to-access pin codes, delivery may take up to 10 business days. Cash on Delivery is not available for all pin codes.'
        },
        {
            "id": "doc_003",
            "topic": "Payment Methods & EMI Options",
            "text": 'ShopEasy accepts a wide range of payment methods to make shopping convenient for all customers. Accepted payment options include credit cards (Visa, Mastercard, RuPay, Amex), debit cards, net banking from over 50 banks, UPI (including Google Pay, PhonePe, Paytm, and BHIM), ShopEasy Wallet, and Cash on Delivery (COD). Cash on Delivery is available for orders up to Rs.10,000 and for eligible pin codes. COD orders require a Rs.30 handling fee. This fee is non-refundable. ShopEasy offers No-Cost EMI on orders above Rs.3,000 through select credit cards from HDFC Bank, ICICI Bank, SBI, Axis Bank, and Kotak Mahindra Bank. EMI tenures available are 3, 6, 9, and 12 months. The EMI interest is subvented by the bank or brand, meaning customers pay no extra charges. Standard EMI with interest is also available through most major credit cards for orders above Rs.1,500. Debit card EMI is available on select Axis Bank and HDFC Bank debit cards for orders above Rs.2,000. Bajaj Finserv and other BNPL options are also accepted at checkout. All payment transactions on ShopEasy are secured with 256-bit SSL encryption. ShopEasy does not store full card details on its servers.'
        },
        {
            "id": "doc_004",
            "topic": "Order Cancellation",
            "text": 'Customers can cancel an order on ShopEasy at any time before the order is shipped. To cancel, go to My Orders, select the order, and click Cancel Order. For orders with multiple items, individual items can be cancelled separately. Once an order has been marked as Shipped, it cannot be cancelled directly. In such cases, customers must wait for delivery and then initiate a return request. For prepaid orders that are cancelled before shipping, the refund is processed within 3 to 5 business days to the original payment method. For COD orders, no refund is applicable as payment has not yet been made. If a seller cancels your order due to stock unavailability or other reasons, ShopEasy will notify you via email and SMS, and a full refund will be issued immediately for prepaid orders. Repeated cancellations by a customer may affect their ability to use the Cash on Delivery option in the future. Customers with a history of more than 3 COD order cancellations in a 30-day period may temporarily lose access to the COD payment option. For bulk or wholesale orders, cancellation must be requested within 2 hours of placing the order.'
        },
        {
            "id": "doc_005",
            "topic": "Product Authenticity & Quality Guarantee",
            "text": 'ShopEasy is committed to selling only genuine, authentic products. All sellers on the ShopEasy platform are required to pass a verification process that includes business registration checks, brand authorisation letters, and product quality audits before they can list products for sale. ShopEasy partners directly with brands and authorised distributors for categories such as electronics, branded fashion, beauty, and health and wellness. Products sold under the ShopEasy Fulfilled tag are stored in ShopEasy own warehouses and undergo additional quality inspection before dispatch. If a customer receives a product they suspect to be counterfeit or not as described, they should immediately report it by raising a complaint through My Orders or by calling customer support. ShopEasy will investigate the complaint within 3 business days and if the claim is validated, will offer a full refund, replacement, or store credit as compensation. ShopEasy also maintains a dedicated quality assurance team that conducts random spot-checks across product listings, and sellers found violating authenticity standards are permanently delisted from the platform.'
        },
        {
            "id": "doc_006",
            "topic": "ShopEasy Wallet & Loyalty Points",
            "text": 'The ShopEasy Wallet is a digital wallet built into every customer account. It can be loaded using any accepted payment method and used for purchases, partial payments, or to receive refunds. The wallet supports a maximum balance of Rs.20,000 at any time. Wallet money cannot be transferred to bank accounts directly by the customer, but refund wallet credits can be withdrawn to the linked bank account by contacting support. ShopEasy Loyalty Points branded as ShopEasy Coins are earned on every eligible purchase. Customers earn 1 ShopEasy Coin for every Rs.100 spent. ShopEasy Coins can be redeemed at a rate of 1 Coin = Rs.0.25 during checkout, up to a maximum discount of 10% of the cart value per transaction. ShopEasy Coins expire 12 months from the date they are earned if not used. Coins earned through referrals or promotions expire in 90 days. ShopEasy also runs a tiered membership programme: Silver (default), Gold (Rs.20,000+ spent in a year), and Platinum (Rs.60,000+ spent in a year). Gold members earn 1.5x ShopEasy Coins and get priority customer support. Platinum members earn 2x coins, get free express delivery on all orders, and receive exclusive early access to sales.'
        },
        {
            "id": "doc_007",
            "topic": "How to Track Your Order",
            "text": 'After placing an order on ShopEasy, customers can track their delivery in real time through multiple channels. Once the order is shipped, an SMS and email notification is sent with a tracking link and the courier partner consignment number. To track an order through the ShopEasy website or app, log in to your account, go to My Orders, select the order, and click Track Order. This shows the current status of the shipment, including whether it is in-transit, out for delivery, or delivered. Estimated delivery dates are shown on the tracking page and are updated dynamically based on courier data. If the tracking page shows no updates for more than 3 business days after dispatch, customers should contact ShopEasy customer support. Our support team will raise a trace request with the courier partner and provide an update within 48 hours. In case the tracking shows Delivered but the customer has not received the package, they must report it within 48 hours of the delivery timestamp. ShopEasy will conduct an investigation and resolve the issue within 5 to 7 business days.'
        },
        {
            "id": "doc_008",
            "topic": "Seller Policies & Selling on ShopEasy",
            "text": 'ShopEasy is an open marketplace that allows individual businesses, brands, and manufacturers to sell their products to millions of customers across India. To become a seller, applicants must have a valid GSTIN (Goods and Services Tax Identification Number), a bank account in the business name, and a government-issued address proof. Sellers can register at seller.shopeasy.in by submitting their documents and completing the onboarding process. Once verified, sellers can list products within 48 hours of approval. ShopEasy charges a commission on each sale, which varies by product category, typically ranging from 5% to 20%. There are no monthly listing fees. Sellers can choose between two fulfilment models: self-ship where the seller arranges their own courier, and ShopEasy Fulfilled where inventory is stored in ShopEasy warehouse and ShopEasy handles packing and shipping. ShopEasy Fulfilled sellers benefit from faster delivery promises and higher visibility in search results. Seller payments are settled every 7 days after order delivery and return window closure. Sellers found selling counterfeit products, misrepresenting listings, or engaging in fraudulent activity are permanently banned and may face legal action.'
        },
        {
            "id": "doc_009",
            "topic": "Customer Support & Complaint Resolution",
            "text": 'ShopEasy customer support is available 7 days a week from 8 AM to 10 PM IST. Customers can reach support through the following channels: live chat on the website or app, phone support at 1800-123-4567 (toll-free), and email at support@shopeasy.in. Response time for email queries is within 24 hours on business days. For order-related issues such as wrong items, damaged goods, missing items, or delayed delivery, customers are advised to raise a complaint directly from My Orders for the fastest resolution. ShopEasy follows a three-tier escalation process. Tier 1 is the front-line support agent who handles most queries within one interaction. If unresolved, the query escalates to Tier 2, the dedicated resolutions team, who aim to resolve complex issues within 3 business days. If still unresolved, Tier 3 escalates to the Seller or Logistics Partner for direct intervention, with a resolution commitment of 7 business days. Customers can also access a self-service help centre at help.shopeasy.in. ShopEasy is committed to resolving 95% of complaints within 48 hours. Customers who are unsatisfied with the resolution can escalate their complaint to the National Consumer Helpline at 1915.'
        },
        {
            "id": "doc_010",
            "topic": "Discounts, Coupons & Flash Sales",
            "text": 'ShopEasy regularly runs promotional campaigns, discount events, and flash sales to offer customers the best prices. The biggest annual sales are the ShopEasy Mega Sale in January, the Summer Blowout in April and May, the Independence Day Sale in August, the Big Festive Sale in October coinciding with Dussehra and Diwali, and the Year-End Clearance in December. Discount coupons can be applied at checkout in the Apply Coupon field. Coupons are case-sensitive and single-use unless stated otherwise. Most coupons have a minimum cart value requirement and a maximum discount cap. Coupons cannot be combined with each other but can be used alongside ShopEasy Coins redemptions. Bank offers are available during major sale events, including instant discounts of 5% to 15% on purchases made with specific credit or debit cards from partner banks such as HDFC, SBI, and ICICI. Flash sales feature limited-stock products at deeply discounted prices and typically last between 2 and 24 hours. Flash sale purchases are subject to a strict no-cancellation policy, though returns are still allowed per the standard return policy. Price drop alerts can be activated for any product by clicking Notify Me on the listing.'
        }
    ]

    col=chromadb.Client().create_collection("shopeasy_ui")
    col.add(
        documents=[d["text"] for d in docs],
        embeddings=embedder.encode([d["text"] for d in docs]).tolist(),
        ids=[d["id"] for d in docs],
        metadatas=[{"topic": d["topic"]} for d in docs]
    )

    class State(TypedDict):
        question: str
        messages: List[dict]
        route: str
        retrieved: str
        sources: List[str]
        tool_result: str
        answer: str
        faithfulness: float
        eval_retries: int
        user_name: str

    FT=0.7
    MR=2

    def memory_node(s):
        msgs=s.get("messages", [])
        name=s.get("user_name", "")
        msgs.append({"role": "user", "content": s["question"]})
        msgs=msgs[-6:]
        if "my name is" in s["question"].lower():
            parts=s["question"].lower().split("my name is")
            if len(parts) > 1:
                name=parts[1].strip().split()[0].capitalize()
        return {"messages": msgs, "user_name": name}

    def router_node(s):
        p=f"""Route for e-commerce FAQ bot. Reply ONE word only.
retrieve: question about returns, shipping, payments, orders, tracking, coupons, warranty, exchanges, account, sellers, wallet, loyalty
tool: needs today's date or delivery date calculation
memory_only: greeting, thanks, or chitchat

Question: {s["question"]}
One word: retrieve, tool, or memory_only"""
        r=llm.invoke(p).content.strip().lower().replace(".", "").replace(",", "")
        return {"route": r if r in ["retrieve", "tool", "memory_only"] else "retrieve"}

    def retrieval_node(s):
        res=col.query(query_embeddings=embedder.encode([s["question"]]).tolist(), n_results=3)
        chunks=[f"[{m['topic']}]\n{d.strip()}" for d, m in zip(res["documents"][0], res["metadatas"][0])]
        sources=[m["topic"] for m in res["metadatas"][0]]
        return {"retrieved": "\n\n---\n\n".join(chunks), "sources": sources}

    def skip_node(s):
        return {"retrieved": "", "sources": []}

    def tool_node(s):
        try:
            t=datetime.now()
            result=f"Today: {t.strftime('%A, %d %B %Y')}\nExpress delivery arrives by: {(t+timedelta(days=2)).strftime('%d %B %Y')} (1-2 business days)\nStandard delivery arrives by: {(t+timedelta(days=6)).strftime('%d %B %Y')} (4-6 business days)"
            return {"tool_result": result, "retrieved": "", "sources": ["Date Calculator"]}
        except Exception as e:
            return {"tool_result": f"error: {str(e)}", "retrieved": "", "sources": []}

    def answer_node(s):
        parts=[]
        if s.get("retrieved"):
            parts.append(f"KNOWLEDGE BASE:\n{s['retrieved']}")
        if s.get("tool_result"):
            parts.append(f"TOOL RESULT:\n{s['tool_result']}")
        ctx="\n\n".join(parts)
        name_line=f"Address the customer as {s['user_name']}." if s.get("user_name") else ""
        retry_line="Previous answer flagged. Use only context." if s.get("eval_retries", 0) > 0 else ""
        system=f"""You are ShopEasy customer support assistant. {name_line} {retry_line}
Rule: answer only from the context below. If not in context say: I do not have that information. Please call 1800-123-4567.
Never make up facts.
Context: {ctx if ctx else "No context. Respond warmly to greetings."}"""
        msgs=[{"role": "system", "content": system}]+s.get("messages", [])
        return {"answer": llm.invoke(msgs).content.strip()}

    def eval_node(s):
        if not s.get("retrieved") and not s.get("tool_result"):
            return {"faithfulness": 1.0, "eval_retries": s.get("eval_retries", 0)}
        answer_lower=s.get("answer", "").lower()
        if "do not have that information" in answer_lower or "don't have that information" in answer_lower:
            return {"faithfulness": 1.0, "eval_retries": s.get("eval_retries", 0)}
        try:
            ctx=s.get("retrieved", "") or s.get("tool_result", "")
            r=llm.invoke(f"Rate faithfulness 0-1. Does answer use ONLY context?\nContext:{ctx}\nAnswer:{s['answer']}\nNumber only:").content
            nums=re.findall(r"\d+\.?\d*", r)
            score=max(0.0, min(1.0, float(nums[0]))) if nums else 0.5
        except:
            score=0.5
        return {"faithfulness": score, "eval_retries": s.get("eval_retries", 0)+1}

    def save_node(s):
        msgs=s.get("messages", [])
        msgs.append({"role": "assistant", "content": s["answer"]})
        return {"messages": msgs}

    def rd(s):
        r=s.get("route", "retrieve")
        return "tool" if r=="tool" else "skip" if r=="memory_only" else "retrieve"

    def ed(s):
        return "save" if s.get("faithfulness", 0) >= FT or s.get("eval_retries", 0) >= MR else "answer"

    g=StateGraph(State)
    for name, fn in [("memory", memory_node), ("router", router_node), ("retrieve", retrieval_node),
                     ("skip", skip_node), ("tool", tool_node), ("answer", answer_node),
                     ("eval", eval_node), ("save", save_node)]:
        g.add_node(name, fn)
    g.set_entry_point("memory")
    for a, b in [("memory", "router"), ("retrieve", "answer"), ("skip", "answer"),
                 ("tool", "answer"), ("answer", "eval"), ("save", END)]:
        g.add_edge(a, b)
    g.add_conditional_edges("router", rd, {"retrieve": "retrieve", "skip": "skip", "tool": "tool"})
    g.add_conditional_edges("eval", ed, {"answer": "answer", "save": "save"})
    return g.compile(checkpointer=MemorySaver())

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "thread_id" not in st.session_state:
    st.session_state.thread_id="user_001"

with st.sidebar:
    st.title("ShopEasy Support")
    st.divider()
    st.markdown("I can help you with:")
    for t in ["Returns", "Shipping", "Order Tracking", "Payments", "Cancellations",
              "Warranty", "Account", "Coupons", "Exchanges", "Selling on ShopEasy"]:
        st.markdown(f"- {t}")
    st.divider()
    if st.button("New Conversation", use_container_width=True):
        import time
        st.session_state.messages=[]
        st.session_state.thread_id=f"s_{int(time.time())}"
        st.rerun()
    st.caption("Helpline: 1800-123-4567")
    st.caption("Mon-Sun 8AM to 10PM")

st.title("ShopEasy Customer Support")
st.markdown("Hello! I am your 24/7 assistant. How can I help you today?")

with st.spinner("loading assistant..."):
    agent=load_agent()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q:=st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("thinking..."):
            try:
                config={"configurable": {"thread_id": st.session_state.thread_id}}
                result=agent.invoke({"question": q, "eval_retries": 0}, config=config)
                answer=result["answer"]
                st.markdown(answer)
                if result.get("sources"):
                    with st.expander("sources used"):
                        st.caption(", ".join(result["sources"]))
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Something went wrong. Please call 1800-123-4567.")