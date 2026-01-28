from agno.agent import Agent
from agno.knowledge.chunking.agentic import AgenticChunking
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader
from agno.vectordb.pgvector import PgVector
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.reader.website_reader import WebsiteReader
from agno.models.openai import OpenAIChat
from agno.knowledge.document import Document
import os
from dotenv import load_dotenv

load_dotenv()

text = "**Welcome to Bakso Nusantara**\n*Authentic Indonesian Meatballs, Reimagined for the Modern World*\n\nAt **Bakso Nusantara**, we don’t just serve meatballs—we serve heritage. Rooted in the heart of Indonesian street food culture, our bakso brings together the essence of comfort, warmth, and authenticity in every bowl. Each bite is a reflection of our passion for quality, tradition, and culinary creativity.\n\nFrom humble warungs to global food stages, we are committed to making bakso a world-class experience without losing its soul. Whether you're a lifelong fan or a first-time explorer, our menu is designed to meet you where you are—with flavors that feel both familiar and exciting.\n\n---\n\n### Our Menu & Price List\n\n**1. Classic Beef Bakso** – *IDR 28,000*\nSix pieces of premium beef meatballs served with clear broth, vermicelli noodles, fried shallots, and celery.\n*Add egg or tofu: +IDR 5,000*\n\n**2. Bakso Urat (Tendon Meatballs)** – *IDR 32,000*\nA textured version for those who crave chewiness. Contains chopped tendon for an authentic bite.\n\n**3. Bakso Keju (Cheese-Filled Bakso)** – *IDR 34,000*\nJuicy beef meatballs with a gooey cheese core. Savory and addictive.\n\n**4. Bakso Mercon (Chili Bomb)** – *IDR 34,000*\nSpicy meatballs filled with crushed chili. Served with extra sambal on the side.\n\n**5. Bakso Ayam (Chicken Meatballs)** – *IDR 26,000*\nMade from lean chicken for a lighter, cleaner taste. Perfect for kids and those preferring poultry.\n\n**6. Vegetarian Bakso** – *IDR 30,000*\nPlant-based meatballs made with soy protein, mushrooms, and our signature blend of spices. 100% meat-free.\n\n**7. Bakso Campur (Mixed Combo)** – *IDR 38,000*\nA mix of classic, urat, keju, and mercon. Best seller for first-timers.\n\n**8. Jumbo Bakso Super** – *IDR 40,000*\nOne giant meatball stuffed with egg and minced beef. Served whole, with clear broth.\n\n---\n\n### Side Dishes & Add-ons\n\n- Fried Tofu (Tahu Goreng) – *IDR 6,000*\n- Crispy Wontons – *IDR 8,000*\n- Siomay (Steamed Dumpling) – *IDR 7,000*\n- Boiled Egg – *IDR 5,000*\n- Extra Noodles – *IDR 4,000*\n- Extra Sambal – *Free, on request*\n\n---\n\n### Beverages\n\n- Iced Sweet Tea – *IDR 6,000*\n- Homemade Iced Lemon Tea – *IDR 8,000*\n- Bottled Water – *IDR 5,000*\n- Traditional Herbal Drink (Wedang Jahe) – *IDR 10,000*\n\n---\n\n### Frozen Product Line (Take-Home Packs)\n\n**Frozen Classic Bakso (20 pcs)** – *IDR 65,000*\n**Frozen Urat Bakso (20 pcs)** – *IDR 72,000*\n**Frozen Keju Bakso (10 pcs)** – *IDR 68,000*\n**Frozen Mercon Bakso (10 pcs)** – *IDR 68,000*\n**Signature Broth Mix (1L)** – *IDR 20,000*\n\n---\n\n### Ready-to-Eat Series (Bakso in a Cup)\n\nPerfect for offices, dorms, or travel.\n\n- **Classic Bakso Cup** – *IDR 22,000*\n- **Keju Bakso Cup** – *IDR 25,000*\n- **Mercon Bakso Cup** – *IDR 25,000*\n\nJust add hot water and enjoy within minutes.\n\n---\n\n### Why Choose Us?\n\n- **Premium Ingredients**: We use only certified beef, fresh spices, and no MSG in any of our products.\n- **Modern Hygiene Standards**: Our kitchen and production lines follow HACCP-aligned protocols.\n- **Flexible Format**: Eat-in, takeaway, delivery, or frozen—our products fit every lifestyle.\n- **Franchise-Ready**: Scalable operations and supply chain to support partners across Indonesia and beyond.\n\n---\n\n**Bakso Nusantara**\n*Tradition in every bite. Innovation in every bowl.*\n\nWe invite you to taste the evolution of bakso."
api_key = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
COLLECTION_NAME = "agent-knowledge"

vector_db = Qdrant(
    collection=COLLECTION_NAME,
    url=qdrant_url,
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small",
        dimensions=1536  # Explicitly set
    ),
    api_key=api_key, # (optional)
)

# Create a knowledge base with Qdrant
knowledge = Knowledge(
    vector_db=vector_db,
    max_results=4
)


# client = QdrantClient(
#     url=qdrant_url,
#     api_key=api_key
# )

# client.create_payload_index(
#     collection_name="agent-knowledge",
#     field_name="content_hash",
#     field_schema=models.PayloadSchemaType.KEYWORD
# )

# print("content_hash index created")

# Add content to the knowledge base
website_reader = WebsiteReader().read(url="https://houpe.id")
print(website_reader)

chunked_document = knowledge._chunk_documents_sync(
    documents=website_reader,
    reader=TextReader(
        chunking_strategy=AgenticChunking(
            model=OpenAIChat(id="gpt-4o-mini"), 
            max_chunk_size=600  # Lebih kecil untuk testing
        )
    )
)
# chunking_strategy=SemanticChunking(
#             chunk_size=600,
#             similarity_threshold=0.5,
#         )
# chunked_document = chunking_strategy.chunk(
#     document=
#         Document(
#             content=text,
#             meta_data={
#                 "source": "web",
#                 "title": "baksonusantara"
#             }
#         )
# )

print(f"Total chunks: {len(chunked_document)}")
for i, doc in enumerate(chunked_document):
    print("=" * 80)
    print(f"📄 Chunk #{i+1}")
    print(f"🧠 Length: {len(doc.content)} chars")
    print(f"🏷 Metadata: {doc.meta_data}")
    print("-" * 80)
    print(doc.content.strip())
    print()
