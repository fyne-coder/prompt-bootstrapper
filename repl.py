from dotenv import load_dotenv
load_dotenv()                            # pick up .env if you’re using it

from api.nodes.new_pipeline.prompt_draft_node import PromptDraftNode

# Sample business text + framework plan
business_text = (
"Fyne LLC is an AI advisory business empowering SMBs "
"to harness data-driven intelligence and grow revenue."
)

framework_plan = {'Marketing':3,'Sales':2,'Success':2,'Product':2,'Ops':1}

prompts = PromptDraftNode(business_text, framework_plan)
print(f"Generated {len(prompts)} prompts:")

for p in prompts[:5]:
   print(" •", p)
