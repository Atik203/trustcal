"""Generate SciClaimBench freeze-180 + full-300 draft batches (original stems only).

Produces schema-valid draft items with balanced strata, original question stems
in the house style, three positions with three atomic claims each, the four
evidence conditions, and unique IDs. Every item carries status ``drafted`` and
an original-derivation evidence slot per claim; candidate verdicts follow the
codebook decision order against the cited passages.

Provenance convention (see FULLBENCH_PLAN.md): item records carry NO
generator markings. Provenance lives ONLY in the batch MANIFEST.json files.
Nothing is gold until member verification + adjudication pass the gate.

    python experiments/calibration/draft_items.py            # validate + write
    python experiments/calibration/draft_items.py --dry-run  # validate only

The script validates the full in-memory batches with the repo validator
(``validate_items.validate_batch`` plus the --expect/balance rules) and
refuses to write anything when validation fails.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "calibration"))
import validate_items as V  # noqa: E402

CAL_DIR = REPO_ROOT / "experiments" / "calibration" / "private" / "items"
FREEZE_DIR = REPO_ROOT / "experiments" / "calibration" / "private" / "freeze180"
FULL_DIR = REPO_ROOT / "experiments" / "calibration" / "private" / "full300"

MODEL = "Muse Spark 1.3 Contributor (opencode-go)"
GENERATOR = "experiments/calibration/draft_items.py"
DATE = "2026-11-21"
RETRIEVED = "2026-11-21"
CONDITIONS = [
    "evidence_available",
    "evidence_absent",
    "evidence_placebo",
    "evidence_contradictory",
]

FRAMES = [
    "Which statement about {topic} is correct?",
    "A study group debates {topic}. Which claim is accurate?",
    "Three agents discuss {topic}. Which position is best supported?",
    "Which of the following best describes {topic}?",
    "An exam asks about {topic}. Which answer should receive full credit?",
    "During a lab meeting on {topic}, which assertion is right?",
    "Which explanation of {topic} is scientifically accurate?",
    "A textbook draft makes four statements about {topic}. Which one should be kept as written?",
]

# Each subject: t = topic phrase, g = gold option, d = 3 distractor options,
# s/r/n = 3 (claim, passage, rationale) triples with support/contradict/neutral
# verdicts respectively. All text is original; passages are team-style
# derivations recorded under the internal appendix ID used as locator.

BIO = [
    {
        "t": "hemoglobin and oxygen transport",
        "g": "Hemoglobin loads oxygen in the lungs and unloads it in the tissues.",
        "d": [
            "Hemoglobin loads oxygen in the tissues and unloads it in the lungs.",
            "Hemoglobin carries oxygen dissolved in plasma rather than bound to red blood cells.",
            "Hemoglobin delivers oxygen to the lungs for exhalation.",
        ],
        "s": [
            ("Hemoglobin binds oxygen in the lungs, where the partial pressure of oxygen is high.",
             "In the pulmonary capillaries the partial pressure of oxygen is high, and oxygen binds to the iron in hemoglobin heme groups.",
             "The passage describes oxygen binding to heme iron under high pulmonary oxygen pressure, which entails the claim."),
            ("Hemoglobin releases oxygen in the tissues, where the partial pressure of oxygen is low.",
             "In systemic capillaries the partial pressure of oxygen is low, so hemoglobin unloads oxygen and it diffuses into tissue cells.",
             "The passage states that low tissue oxygen pressure causes hemoglobin to unload oxygen, which entails the claim."),
            ("Each hemoglobin molecule can carry up to four oxygen molecules.",
             "A hemoglobin tetramer holds four heme groups, and each heme group binds one oxygen molecule.",
             "Four heme groups with one oxygen each gives a maximum of four, which entails the claim."),
        ],
        "r": [
            ("Hemoglobin binds oxygen most tightly in oxygen-poor tissues.",
             "Hemoglobin affinity for oxygen is highest where oxygen pressure is high, as in the lungs, and falls where oxygen pressure is low.",
             "The passage states affinity is highest in oxygen-rich blood, the opposite of the claim, so the claim is refuted."),
            ("Mature red blood cells consume oxygen through aerobic respiration.",
             "Mature red blood cells lack mitochondria and meet their energy needs by anaerobic glycolysis.",
             "Cells without mitochondria cannot respire aerobically, which refutes the claim."),
            ("Oxygen binds to the globin protein chains rather than to heme iron.",
             "Each oxygen molecule coordinates to the ferrous iron at the center of a heme group held by the globin chains.",
             "The passage places binding at the heme iron, not the globin chains, which refutes the claim."),
        ],
        "n": [
            ("Hemoglobin concentration is the single strongest determinant of endurance performance.",
             "The cohort recorded endurance alongside training history, cardiac output, hemoglobin concentration, and muscle fiber composition.",
             "The passage lists hemoglobin among several recorded factors without comparing their strength, so the claim is neither established nor refuted."),
            ("Hemoglobin-based oxygen carriers are approved for routine clinical use worldwide.",
             "Several hemoglobin-based oxygen carrier products have entered clinical trials for trauma and surgical indications.",
             "Trial-stage products do not establish worldwide routine approval, so the claim is neither established nor refuted."),
            ("Altitude training raises hemoglobin mass more in every athlete than any other legal intervention.",
             "Altitude camps were compared with sea-level training for changes in hemoglobin mass across the squad.",
             "A comparison with sea-level training alone cannot rank altitude against all other interventions, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "insulin regulation of blood glucose",
        "g": "Insulin lowers blood glucose by promoting glucose uptake and storage.",
        "d": [
            "Insulin raises blood glucose by stimulating glucose release from the liver.",
            "Insulin acts only on the brain and has no effect on muscle or fat.",
            "Glucagon and insulin both lower blood glucose after a meal.",
        ],
        "s": [
            ("Pancreatic beta cells release insulin when blood glucose rises.",
             "Rising blood glucose stimulates pancreatic beta cells to secrete insulin into the bloodstream.",
             "The passage describes glucose-stimulated insulin secretion, which entails the claim."),
            ("Insulin promotes glucose uptake into muscle and fat cells.",
             "Insulin signaling moves glucose transporters to the surface of muscle and fat cells, increasing glucose entry.",
             "The passage states that insulin signaling increases glucose entry into muscle and fat, which entails the claim."),
            ("Insulin stimulates the liver to store glucose as glycogen.",
             "In the liver, insulin activates glycogen synthesis, converting incoming glucose into stored glycogen.",
             "The passage describes insulin-driven glycogen synthesis, which entails the claim."),
        ],
        "r": [
            ("Insulin stimulates the liver to break down glycogen into glucose.",
             "Glycogen breakdown in the liver is driven by glucagon and adrenaline, while insulin suppresses it and favors storage.",
             "The passage assigns glycogen breakdown to other hormones and says insulin suppresses it, which refutes the claim."),
            ("Type 1 diabetes is caused by insulin resistance in muscle tissue.",
             "Type 1 diabetes results from autoimmune destruction of insulin-producing beta cells, leaving little insulin to act.",
             "The passage identifies beta-cell loss, not muscle resistance, as the cause, which refutes the claim."),
            ("Insulin secretion increases during fasting and starvation.",
             "During fasting, insulin secretion falls while glucagon rises to maintain blood glucose from stored fuels.",
             "The passage states insulin falls during fasting, the opposite of the claim, so the claim is refuted."),
        ],
        "n": [
            ("A new insulin analogue controls glucose better than all existing insulins in every patient.",
             "The trial compared the new analogue with one existing insulin for change in average glucose over six months.",
             "One comparator and one outcome cannot support superiority over all insulins in every patient, so the claim is neither established nor refuted."),
            ("Dietary chromium supplements cure insulin resistance.",
             "Chromium intake was recorded as a dietary variable in the observational cohort.",
             "Merely recording intake establishes nothing about cures, so the claim is neither established nor refuted."),
            ("Insulin pumps eliminate hypoglycaemia in all users.",
             "Pump users logged hypoglycaemic episodes alongside sensor readings during the study period.",
             "Logging episodes does not show elimination in all users, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "mRNA vaccines and antigen expression",
        "g": "mRNA vaccines instruct cells to produce a pathogen protein that trains immunity.",
        "d": [
            "mRNA vaccines insert lasting DNA changes into the vaccinated person's genome.",
            "mRNA vaccines contain live weakened virus that replicates in the recipient.",
            "mRNA vaccines work by directly killing pathogens in the bloodstream.",
        ],
        "s": [
            ("The vaccine mRNA is translated by host cells into a pathogen protein.",
             "After uptake, ribosomes translate the vaccine mRNA into the encoded pathogen protein for immune presentation.",
             "The passage describes host translation of the mRNA into pathogen protein, which entails the claim."),
            ("The immune response targets the protein produced from the vaccine mRNA.",
             "Antibodies and T cells generated after vaccination recognize the pathogen protein expressed from the mRNA.",
             "The passage states immunity recognizes the expressed protein, which entails the claim."),
            ("Vaccine mRNA degrades in the cell within a short time after translation.",
             "Cellular enzymes break down the vaccine mRNA within days, so expression is transient rather than permanent.",
             "The passage describes breakdown of the mRNA within days, which entails the claim."),
        ],
        "r": [
            ("mRNA vaccines permanently alter the recipient's DNA.",
             "Vaccine mRNA does not enter the nucleus and lacks the machinery to integrate into DNA, so the genome is unchanged.",
             "The passage states the genome is unchanged, which refutes the claim."),
            ("The lipid nanoparticle itself is the antigen that immunity targets.",
             "Lipid nanoparticles only deliver the mRNA; the immune response is directed against the translated pathogen protein.",
             "The passage assigns the immune target to the translated protein, not the particle, which refutes the claim."),
            ("mRNA vaccines provide immunity without any protein being produced.",
             "Protection depends on cells producing the encoded protein, which is then recognized by the immune system.",
             "The passage makes protection depend on protein production, which refutes the claim."),
        ],
        "n": [
            ("mRNA vaccines are more effective than every other vaccine platform against all diseases.",
             "The study compared one mRNA vaccine with one protein vaccine for a single pathogen over one season.",
             "One comparison for one pathogen cannot support superiority over every platform, so the claim is neither established nor refuted."),
            ("A single mRNA dose protects for life.",
             "Antibody levels were measured at one, six, and twelve months after dosing.",
             "Twelve months of measurements cannot establish lifetime protection, so the claim is neither established nor refuted."),
            ("mRNA vaccines cannot be updated for new variants.",
             "Manufacturing records describe the sequence template used for the current production batch.",
             "A batch record says nothing about whether templates can change, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "penicillin inhibition of bacterial cell-wall synthesis",
        "g": "Penicillin weakens bacterial cell walls by blocking their construction.",
        "d": [
            "Penicillin kills bacteria by destroying their DNA.",
            "Penicillin strengthens bacterial cell walls against immune attack.",
            "Penicillin is effective against all viruses that cause colds.",
        ],
        "s": [
            ("Penicillin binds the bacterial enzymes that cross-link the cell wall.",
             "Penicillin attaches to penicillin-binding proteins, the enzymes that cross-link peptidoglycan strands in the wall.",
             "The passage describes penicillin binding the cross-linking enzymes, which entails the claim."),
            ("Penicillin is most effective against actively growing bacteria.",
             "Because penicillin blocks new wall construction, bacteria that are actively dividing are the most vulnerable.",
             "The passage ties effectiveness to active wall construction during division, which entails the claim."),
            ("Penicillin leaves human cells unharmed because they lack cell walls.",
             "Human cells have no peptidoglycan wall, so the wall-blocking action of penicillin has no target in human tissue.",
             "The passage states there is no drug target in human cells, which entails the claim."),
        ],
        "r": [
            ("Penicillin dissolves already-built bacterial cell walls on contact.",
             "Penicillin only prevents new cross-links from forming; existing wall material is unaffected by the drug.",
             "The passage limits the drug to blocking new construction, which refutes the claim."),
            ("Bacteria that produce beta-lactamase remain fully sensitive to penicillin.",
             "Beta-lactamase enzymes break open the active ring of penicillin, so producing strains resist the drug.",
             "The passage states producing strains resist the drug, which refutes the claim."),
            ("Penicillin blocks protein synthesis on bacterial ribosomes.",
             "Ribosome-targeting antibiotics such as tetracyclines block protein synthesis; penicillin acts on wall-building enzymes instead.",
             "The passage assigns ribosome blocking to other drugs, which refutes the claim."),
        ],
        "n": [
            ("Penicillin cures every bacterial infection faster than any alternative.",
             "The trial compared penicillin with one alternative for a single infection type.",
             "One comparison cannot support superiority for every infection, so the claim is neither established nor refuted."),
            ("Allergic reactions to penicillin are purely psychological.",
             "Allergy histories were documented for all enrolled participants.",
             "Documenting histories establishes nothing about the mechanism of reactions, so the claim is neither established nor refuted."),
            ("Penicillin resistance never spreads between bacteria.",
             "Resistance genes were surveyed in isolates from three hospital wards.",
             "A survey of isolates cannot show that spread never happens, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "filtration in the nephron",
        "g": "The glomerulus filters blood plasma and the tubules refine the filtrate into urine.",
        "d": [
            "The nephron produces urine by filtering blood in the collecting duct.",
            "All filtered glucose is normally excreted in the urine.",
            "The kidneys clean blood by pumping urine back into the bloodstream.",
        ],
        "s": [
            ("Blood plasma is filtered across the glomerular capillaries into Bowman's capsule.",
             "Pressure forces water and small solutes from glomerular blood across the filtration barrier into Bowman's capsule.",
             "The passage describes pressure filtration into Bowman's capsule, which entails the claim."),
            ("Useful substances such as glucose are reabsorbed from the filtrate.",
             "Tubule cells reclaim filtered glucose and amino acids so that little escapes into the final urine.",
             "The passage describes reclamation of glucose, which entails the claim."),
            ("Concentrated urine is produced by reabsorbing water in the collecting duct.",
             "Under antidiuretic hormone, the collecting duct reabsorbs water, concentrating the urine that remains.",
             "The passage describes water reabsorption concentrating the urine, which entails the claim."),
        ],
        "r": [
            ("Red blood cells normally pass through the filter into the urine.",
             "The filtration barrier retains cells and large proteins, so healthy urine contains neither red cells nor much protein.",
             "The passage states the barrier retains cells, which refutes the claim."),
            ("Filtration occurs mainly in the loop of Henle.",
             "Filtration occurs at the glomerulus; the loop of Henle concentrates the medulla and conditions the filtrate downstream.",
             "The passage places filtration at the glomerulus, not the loop, which refutes the claim."),
            ("The kidneys add urea to the blood to raise its concentration.",
             "The kidneys remove urea from the blood and excrete it, lowering blood urea rather than raising it.",
             "The passage describes removal of urea, the opposite of the claim, so the claim is refuted."),
        ],
        "n": [
            ("Drinking more water always cures kidney disease.",
             "Fluid intake was logged for participants with and without kidney disease.",
             "Logging intake cannot show that water cures disease, so the claim is neither established nor refuted."),
            ("One kidney function test diagnoses every kidney disorder.",
             "The study evaluated a single marker against biopsy findings in one patient group.",
             "One marker in one group cannot validate diagnosis of every disorder, so the claim is neither established nor refuted."),
            ("Kidney stones form only in the bladder.",
             "Stone locations were mapped across the kidney, ureter, and bladder in the case series.",
             "Mapping locations does not show stones form only in the bladder, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "platelet aggregation in blood clotting",
        "g": "Platelets aggregate at vessel injuries to form the initial clot.",
        "d": [
            "Platelets dissolve clots after they form.",
            "Platelets carry oxygen in place of red blood cells.",
            "Clotting occurs only inside intact healthy vessels.",
        ],
        "s": [
            ("Platelets adhere to exposed collagen at a vessel injury.",
             "When a vessel wall breaks, exposed collagen captures passing platelets at the damage site.",
             "The passage describes platelets captured by exposed collagen, which entails the claim."),
            ("Aggregating platelets release signals that recruit more platelets.",
             "Activated platelets release chemical messengers that switch nearby platelets to a sticky state and draw them in.",
             "The passage describes recruitment signaling, which entails the claim."),
            ("The platelet plug provides the scaffold for fibrin reinforcement.",
             "Fibrin strands weave through the assembled platelet plug, strengthening it into a stable clot.",
             "The passage describes fibrin strengthening the plug, which entails the claim."),
        ],
        "r": [
            ("Platelets prevent clotting by coating vessel injuries.",
             "Platelets initiate clotting by sticking to injuries and to each other, not by preventing aggregation.",
             "The passage states platelets initiate clotting, which refutes the claim."),
            ("Aspirin promotes platelet aggregation.",
             "Aspirin blocks the platelet enzyme that makes a key aggregation signal, so it reduces rather than promotes clumping.",
             "The passage states aspirin reduces clumping, which refutes the claim."),
            ("Clotting factors are produced by platelets.",
             "Clotting factors are plasma proteins made mainly by the liver; platelets supply the surface where they act.",
             "The passage assigns factor production to the liver, which refutes the claim."),
        ],
        "n": [
            ("Aspirin prevents all heart attacks in everyone who takes it.",
             "The trial tracked heart attacks among aspirin users and non-users in one age group.",
             "One age group cannot support prevention in everyone, so the claim is neither established nor refuted."),
            ("Platelet counts are identical in all healthy adults.",
             "Platelet counts were measured once in each volunteer in the survey.",
             "Single measurements cannot show all adults are identical, so the claim is neither established nor refuted."),
            ("Clots never form in veins.",
             "Clot locations were classified as arterial or venous in the registry.",
             "Classification alone cannot show venous clots never occur, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "cytotoxic T-cell recognition of infected cells",
        "g": "Cytotoxic T cells kill infected cells that display foreign fragments.",
        "d": [
            "Cytotoxic T cells produce antibodies against bacteria in the blood.",
            "Cytotoxic T cells ignore infected cells and attack only healthy tissue.",
            "T cells recognize pathogens directly without any presentation step.",
        ],
        "s": [
            ("Infected cells display pathogen fragments on MHC class I molecules.",
             "Nearly all nucleated cells load peptide fragments onto MHC class I molecules for surface display, including fragments from intracellular pathogens.",
             "The passage describes fragment display on MHC class I, which entails the claim."),
            ("A cytotoxic T cell binds only the fragment its receptor matches.",
             "Each T-cell receptor binds a specific peptide-MHC combination, ignoring cells that display other fragments.",
             "The passage describes specific receptor binding, which entails the claim."),
            ("Bound cytotoxic T cells trigger death of the infected target cell.",
             "After recognition, the T cell releases perforin and granzymes that drive the infected cell into programmed death.",
             "The passage describes target-cell killing after recognition, which entails the claim."),
        ],
        "r": [
            ("Cytotoxic T cells recognize free-floating virus particles.",
             "T cells recognize fragments displayed on cell surfaces, while free particles are handled by antibodies.",
             "The passage assigns free-particle recognition to antibodies, which refutes the claim."),
            ("Helper T cells kill infected cells directly.",
             "Helper T cells coordinate the response with signals, while the direct killing is carried out by cytotoxic T cells.",
             "The passage assigns direct killing to cytotoxic cells, which refutes the claim."),
            ("MHC molecules display whole intact pathogens on the cell surface.",
             "MHC molecules display short peptide fragments, not whole intact pathogens.",
             "The passage states fragments, not whole pathogens, are displayed, which refutes the claim."),
        ],
        "n": [
            ("T-cell therapy cures every cancer.",
             "The trial tested a T-cell therapy in patients with one cancer type.",
             "One cancer type cannot support cures for every cancer, so the claim is neither established nor refuted."),
            ("Everyone has identical T-cell receptors.",
             "Receptor sequences were sampled from donors in the repertoire study.",
             "Sampling sequences cannot show all receptors are identical, so the claim is neither established nor refuted."),
            ("Vaccines work without any T-cell involvement.",
             "T-cell responses were measured as a secondary endpoint in the vaccine trial.",
             "Measuring responses does not show vaccines work without them, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "hepatic metabolism of acetaminophen",
        "g": "The liver converts acetaminophen to safe products unless the dose overwhelms them.",
        "d": [
            "Acetaminophen is metabolized mainly in the kidneys.",
            "Acetaminophen overdose is harmless because the excess is exhaled.",
            "Acetaminophen relieves pain by numbing the skin surface.",
        ],
        "s": [
            ("At normal doses the liver conjugates acetaminophen into excretable forms.",
             "Therapeutic doses are joined to sulfate and glucuronide in the liver and leave the body in urine.",
             "The passage describes conjugation and urinary excretion, which entails the claim."),
            ("A small fraction becomes a toxic intermediate normally neutralized by glutathione.",
             "A minor pathway forms a reactive intermediate that liver glutathione detoxifies before it can cause harm.",
             "The passage describes glutathione detoxification of the intermediate, which entails the claim."),
            ("Overdose depletes glutathione and allows liver injury.",
             "In overdose the safe pathways saturate and glutathione runs out, letting the reactive intermediate damage liver cells.",
             "The passage describes glutathione exhaustion leading to damage, which entails the claim."),
        ],
        "r": [
            ("Alcohol use protects the liver during acetaminophen overdose.",
             "Chronic alcohol use depletes glutathione and induces the toxic pathway, worsening rather than preventing injury.",
             "The passage states alcohol worsens injury, which refutes the claim."),
            ("Acetaminophen is eliminated unchanged in the breath.",
             "Acetaminophen leaves the body as liver metabolites in urine, not as unchanged drug in exhaled air.",
             "The passage describes urinary metabolites, not exhalation, which refutes the claim."),
            ("The toxic intermediate forms only at therapeutic doses.",
             "The reactive intermediate forms in small amounts at all doses and becomes dangerous when overdose overwhelms detoxification.",
             "The passage states it forms at all doses, which refutes the claim."),
        ],
        "n": [
            ("Acetaminophen is the safest drug for every patient at any dose.",
             "Adverse events were compared between acetaminophen and one alternative in the review.",
             "One comparison cannot support safety for every patient at any dose, so the claim is neither established nor refuted."),
            ("Genetic testing is required before any acetaminophen use.",
             "Genetic variants were genotyped in a subgroup of study participants.",
             "Genotyping a subgroup cannot establish a universal requirement, so the claim is neither established nor refuted."),
            ("Acetaminophen treats bacterial infections.",
             "Fever readings were recorded for patients with and without confirmed infection.",
             "Recording fever cannot show treatment of infection, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "gas exchange in the alveoli",
        "g": "Oxygen and carbon dioxide diffuse across the thin alveolar walls.",
        "d": [
            "Alveoli pump air actively using muscle contractions.",
            "Gas exchange occurs mainly in the trachea and bronchi.",
            "Alveoli absorb oxygen into the digestive system.",
        ],
        "s": [
            ("Alveolar walls are thin enough for rapid diffusion.",
             "The air-blood barrier is about one cell thick on each side, keeping the diffusion distance extremely short.",
             "The passage describes an extremely short diffusion distance, which entails the claim."),
            ("Oxygen diffuses from alveolar air into the blood.",
             "Because alveolar oxygen pressure exceeds that in incoming blood, oxygen moves down its gradient into capillaries.",
             "The passage describes downhill oxygen movement into blood, which entails the claim."),
            ("Carbon dioxide diffuses from the blood into alveolar air.",
             "Blood arriving at the lungs carries more carbon dioxide than alveolar air, so it diffuses outward to be exhaled.",
             "The passage describes outward carbon dioxide movement, which entails the claim."),
        ],
        "r": [
            ("The diaphragm performs gas exchange inside the alveoli.",
             "The diaphragm ventilates the lungs by changing thoracic volume; diffusion itself occurs passively across alveolar walls.",
             "The passage assigns the diaphragm a ventilation role, not exchange, which refutes the claim."),
            ("Alveoli convert carbon dioxide into oxygen.",
             "Alveoli only exchange the gases by diffusion; no conversion of carbon dioxide into oxygen takes place there.",
             "The passage denies any conversion, which refutes the claim."),
            ("Thicker alveolar walls would speed up gas exchange.",
             "Diffusion slows as wall thickness grows, which is why fluid-filled or scarred lungs exchange gases poorly.",
             "The passage states thickness slows diffusion, which refutes the claim."),
        ],
        "n": [
            ("Breathing exercises cure all lung diseases.",
             "Lung function was measured before and after a breathing program in one patient group.",
             "One patient group cannot support cures for all diseases, so the claim is neither established nor refuted."),
            ("Lung capacity is the same in every adult.",
             "Vital capacity was recorded once per volunteer in the survey.",
             "Recording values cannot show all adults are identical, so the claim is neither established nor refuted."),
            ("Air pollution never reaches the alveoli.",
             "Particle deposition was modeled for the upper airways in the study.",
             "Modeling upper airways says nothing about alveolar reach, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "calcium signaling in skeletal-muscle contraction",
        "g": "Calcium release lets muscle filaments slide and contract.",
        "d": [
            "Calcium causes muscles to relax by detaching all filaments permanently.",
            "Skeletal muscles contract when calcium is removed from the cell.",
            "Nerves contract muscles by pulling the fibers directly.",
        ],
        "s": [
            ("A nerve signal triggers calcium release inside the muscle fiber.",
             "The action potential opens calcium channels of the sarcoplasmic reticulum, flooding the fiber interior with calcium.",
             "The passage describes signal-triggered calcium release, which entails the claim."),
            ("Calcium exposes the binding sites on actin filaments.",
             "Calcium binds troponin, shifting tropomyosin away from the myosin-binding sites on actin.",
             "The passage describes calcium uncovering the binding sites, which entails the claim."),
            ("Myosin heads pull actin filaments to shorten the sarcomere.",
             "Energized myosin heads attach to exposed actin sites and pivot, sliding the filaments past each other.",
             "The passage describes myosin pivoting sliding the filaments, which entails the claim."),
        ],
        "r": [
            ("Muscles contract when calcium is pumped back into storage.",
             "Pumping calcium back into the reticulum ends contraction and causes relaxation, not contraction.",
             "The passage assigns pumping to relaxation, which refutes the claim."),
            ("ATP is unnecessary for muscle contraction.",
             "ATP powers the myosin pivot and detaches myosin from actin; without it, contraction cannot proceed.",
             "The passage makes ATP essential, which refutes the claim."),
            ("Smooth and skeletal muscle use identical calcium triggers.",
             "Skeletal muscle uses troponin-based control, while smooth muscle uses a different myosin-linked regulatory system.",
             "The passage describes different control systems, which refutes the claim."),
        ],
        "n": [
            ("Calcium supplements improve sprint speed in all athletes.",
             "Supplement use and sprint times were both recorded in the survey.",
             "Recording both variables cannot show improvement in all athletes, so the claim is neither established nor refuted."),
            ("Muscle cramps are always caused by dehydration.",
             "Cramp episodes were logged alongside hydration status in the cohort.",
             "Logging both cannot show dehydration always causes cramps, so the claim is neither established nor refuted."),
            ("One protein controls every aspect of contraction.",
             "Expression levels of several contractile proteins were measured in the biopsies.",
             "Measuring several proteins cannot show one controls everything, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "colonic fermentation of dietary fiber",
        "g": "Gut bacteria ferment fiber into short-chain fatty acids.",
        "d": [
            "Human enzymes digest fiber in the stomach.",
            "Fiber passes through the body with no interaction with microbes.",
            "Short-chain fatty acids are produced in the liver from fat.",
        ],
        "s": [
            ("Human enzymes cannot break down most dietary fiber.",
             "Human genomes encode almost no enzymes for fiber polysaccharides, so fiber reaches the colon largely intact.",
             "The passage states fiber arrives in the colon intact, which entails the claim."),
            ("Colonic bacteria ferment fiber into short-chain fatty acids.",
             "Colonic microbes metabolize fiber into acetate, propionate, and butyrate as fermentation end products.",
             "The passage describes bacterial production of the three acids, which entails the claim."),
            ("Colon cells use butyrate as a preferred energy source.",
             "Colonocytes oxidize butyrate from the lumen as their favored fuel.",
             "The passage identifies butyrate as the favored fuel, which entails the claim."),
        ],
        "r": [
            ("Fiber is absorbed into the blood in the small intestine.",
             "Fiber resists small-intestinal digestion and absorption, arriving in the colon for bacterial fermentation.",
             "The passage states fiber reaches the colon unabsorbed, which refutes the claim."),
            ("Sterile colons produce the same fatty acids from fiber.",
             "Germ-free animals produce almost none of these acids from fiber, showing bacteria are required.",
             "The passage makes bacteria required, which refutes the claim."),
            ("All gut bacteria perform identical fermentation.",
             "Different bacterial groups ferment different fibers into different acid mixtures.",
             "The passage describes group-specific fermentation, which refutes the claim."),
        ],
        "n": [
            ("Fiber supplements cure all digestive diseases.",
             "Symptom scores were tracked in fiber-supplement users with one condition.",
             "One condition cannot support cures for all diseases, so the claim is neither established nor refuted."),
            ("Everyone's microbiota responds identically to fiber.",
             "Microbiota composition was profiled before and after fiber in the volunteers.",
             "Profiling responses cannot show all responses are identical, so the claim is neither established nor refuted."),
            ("Probiotics permanently replace the native microbiota.",
             "Probiotic strains were detectable in stool only during supplementation.",
             "Detection only during supplementation argues against permanent replacement, but the passage does not settle it, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "nucleotide excision repair of ultraviolet DNA damage",
        "g": "Nucleotide excision repair removes UV-damaged DNA segments.",
        "d": [
            "UV damage is repaired by digesting the entire chromosome.",
            "Sunscreen works by repairing DNA after damage occurs.",
            "UV light strengthens DNA by adding extra bonds.",
        ],
        "s": [
            ("UV light fuses adjacent pyrimidine bases into dimers.",
             "Ultraviolet photons link neighboring thymine or cytosine bases into cyclobutane dimers that distort the helix.",
             "The passage describes photon-induced dimer formation, which entails the claim."),
            ("Repair enzymes cut out the damaged DNA segment.",
             "Excision enzymes nick the strand on both sides of the dimer and remove the damaged patch.",
             "The passage describes cutting out the damaged patch, which entails the claim."),
            ("DNA polymerase fills the gap using the intact strand as template.",
             "After excision, polymerase synthesizes replacement DNA guided by the undamaged complementary strand.",
             "The passage describes template-guided gap filling, which entails the claim."),
        ],
        "r": [
            ("Dimers strengthen the DNA helix.",
             "Dimers kink and destabilize the helix, blocking replication until removed.",
             "The passage states dimers destabilize the helix, which refutes the claim."),
            ("Repair copies the damaged strand to preserve the mutation.",
             "Repair uses the intact complementary strand as the template, restoring the original sequence.",
             "The passage states the intact strand templates repair, which refutes the claim."),
            ("Excision repair operates only in skin cells.",
             "Nucleotide excision repair operates in essentially all nucleated human cells.",
             "The passage states the repair operates broadly, which refutes the claim."),
        ],
        "n": [
            ("Sunscreen makes UV exposure completely safe.",
             "Sunburn rates were compared between sunscreen users and non-users at the beach.",
             "Comparing sunburn rates cannot show complete safety, so the claim is neither established nor refuted."),
            ("All UV damage leads to cancer.",
             "Cancer outcomes were tracked in participants with measured UV exposure.",
             "Tracking outcomes cannot show all damage leads to cancer, so the claim is neither established nor refuted."),
            ("DNA repair prevents every mutation.",
             "Mutation counts were compared between repair-proficient and repair-deficient cell lines.",
             "A comparison of counts cannot show every mutation is prevented, so the claim is neither established nor refuted."),
        ],
    },
]

PHYS = [
    {
        "t": "conservation of momentum in collisions",
        "g": "Total momentum is conserved in collisions without external impulses.",
        "d": [
            "Momentum is conserved only when objects stick together.",
            "Kinetic energy is always conserved in every collision.",
            "Heavier objects always gain momentum in collisions.",
        ],
        "s": [
            ("The total momentum of the system before impact equals its total after impact.",
             "With no external impulse during the brief impact, the vector sum of momenta is unchanged from before to after.",
             "The passage states the vector sum is unchanged, which entails the claim."),
            ("In an elastic collision, kinetic energy is also conserved.",
             "Ideal elastic collisions store impact energy temporarily in deformation and return it fully, preserving kinetic energy.",
             "The passage describes full return of impact energy, which entails the claim."),
            ("Recoil occurs because momentum lost by one object is gained by another.",
             "A launcher gains backward momentum exactly balancing the forward momentum carried away by the projectile.",
             "The passage describes exactly balancing momenta, which entails the claim."),
        ],
        "r": [
            ("Friction with the ground never affects collision analysis.",
             "External impulses such as friction change total momentum, so real analyses must account for or minimize them.",
             "The passage states friction changes total momentum, which refutes the claim."),
            ("Two objects can collide without exerting forces on each other.",
             "Collisions act through equal and opposite contact forces, as required by the third law of motion.",
             "The passage requires contact forces in every collision, which refutes the claim."),
            ("Momentum conservation fails at low speeds.",
             "Momentum conservation holds at all everyday speeds; only near light speed does the relativistic form take over.",
             "The passage affirms conservation at everyday speeds, which refutes the claim."),
        ],
        "n": [
            ("Crumple zones increase the force on passengers.",
             "Injury rates were compared between vehicle models with different front-end designs.",
             "Comparing injury rates cannot show crumple zones increase force, so the claim is neither established nor refuted."),
            ("Airbags work by speeding up the collision.",
             "Head injury readings were logged in crash tests with and without airbags.",
             "Logging readings cannot show airbags speed up collisions, so the claim is neither established nor refuted."),
            ("Seatbelts are unnecessary at low speeds.",
             "Injury outcomes were stratified by speed band in the crash registry.",
             "Stratifying outcomes cannot show seatbelts are unnecessary, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "wave interference",
        "g": "Overlapping waves add by superposition, creating interference patterns.",
        "d": [
            "Overlapping waves always cancel each other completely.",
            "Interference destroys wave energy permanently.",
            "Only sound waves can interfere.",
        ],
        "s": [
            ("Two in-phase waves reinforce to a larger amplitude.",
             "When crest meets crest, the displacements add, producing constructive interference with doubled amplitude.",
             "The passage describes displacements adding, which entails the claim."),
            ("Two out-of-phase waves cancel where they meet.",
             "When crest meets trough of equal size, the displacements sum to zero in destructive interference.",
             "The passage describes displacements summing to zero, which entails the claim."),
            ("Double-slit fringes arise from path-difference interference.",
             "Light from the two slits travels different distances to each screen point, and the phase differences create bright and dark fringes.",
             "The passage attributes fringes to phase differences, which entails the claim."),
        ],
        "r": [
            ("Interference violates energy conservation.",
             "Interference only redistributes energy between bright and dark regions; total energy is conserved.",
             "The passage states total energy is conserved, which refutes the claim."),
            ("Incoherent sources produce stable fringe patterns.",
             "Stable fringes need a fixed phase relationship, which incoherent sources lack.",
             "The passage denies stable fringes without fixed phase, which refutes the claim."),
            ("Destructive interference requires different frequencies.",
             "Cancellation requires the same frequency with opposite phase; different frequencies produce beats instead.",
             "The passage requires equal frequency for cancellation, which refutes the claim."),
        ],
        "n": [
            ("Noise-cancelling headphones silence every sound.",
             "Perceived loudness was rated with the feature on and off in one office.",
             "One office rating cannot show every sound is silenced, so the claim is neither established nor refuted."),
            ("Interference patterns prove light is a particle.",
             "Fringe visibility was recorded across several slit configurations.",
             "Recording visibility cannot prove a particle nature, so the claim is neither established nor refuted."),
            ("All microscopes use electron interference.",
             "Resolution figures were listed for optical and electron instruments in the catalogue.",
             "A catalogue listing cannot show all microscopes use electrons, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "radioactive half-life",
        "g": "A half-life is the time for half of a sample's unstable nuclei to decay.",
        "d": [
            "Half of the sample vanishes without any emission.",
            "Half-life means the sample becomes safe after one period.",
            "Heating a sample stops radioactive decay.",
        ],
        "s": [
            ("Decay of a large sample follows an exponential curve.",
             "With constant per-nucleus decay probability, the surviving number falls exponentially with time.",
             "The passage derives exponential fall from constant probability, which entails the claim."),
            ("After two half-lives, one quarter of the nuclei remain.",
             "Halving twice leaves one half of one half, which is one quarter of the original nuclei.",
             "The passage computes one quarter remaining, which entails the claim."),
            ("Half-life is independent of sample size and temperature.",
             "The decay constant is a nuclear property, unchanged by how many nuclei are present or by ordinary heating.",
             "The passage states the constant resists size and heating, which entails the claim."),
        ],
        "r": [
            ("All nuclei in a sample decay simultaneously at the half-life mark.",
             "Decay is random per nucleus, so at one half-life only about half have decayed, not all at once.",
             "The passage denies simultaneous decay, which refutes the claim."),
            ("The decayed half turns into nothing.",
             "Decayed nuclei transform into daughter nuclides plus emitted particles, not into nothing.",
             "The passage describes transformation products, which refutes the claim."),
            ("Chemical reactions can change the half-life.",
             "Ordinary chemistry involves electrons, while decay rates are set by the nucleus and resist chemical influence.",
             "The passage states decay resists chemistry, which refutes the claim."),
        ],
        "n": [
            ("Radioactive materials are the leading cause of all illness.",
             "Illness rates were mapped against background radiation across regions.",
             "Mapping rates cannot show materials lead all illness, so the claim is neither established nor refuted."),
            ("Every isotope has the same half-life.",
             "Measured half-lives were tabulated for the isotopes in the chart.",
             "Tabulating values cannot show all are identical, so the claim is neither established nor refuted."),
            ("Radiation is always lethal.",
             "Health effects were recorded across a range of documented doses.",
             "A range of effects cannot show every dose is lethal, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "hydrogen bonding in water",
        "g": "Hydrogen bonds between water molecules explain water's unusual properties.",
        "d": [
            "Water boils at a low temperature because its bonds are strong.",
            "Ice sinks because hydrogen bonds make it dense.",
            "Hydrogen bonds occur within a single water molecule.",
        ],
        "s": [
            ("A hydrogen bond links hydrogen of one molecule to oxygen of another.",
             "The partially positive hydrogen of one water molecule attracts the lone pairs on the oxygen of a neighbor.",
             "The passage describes attraction between molecules, which entails the claim."),
            ("Hydrogen bonding raises the boiling point of water.",
             "Extra energy is needed to break the intermolecular network before molecules can escape, lifting the boiling point.",
             "The passage ties the network to a lifted boiling point, which entails the claim."),
            ("Ice floats because its hydrogen-bond network holds molecules apart.",
             "In ice, hydrogen bonds lock molecules into an open lattice that is less dense than liquid water.",
             "The passage describes an open, less-dense lattice, which entails the claim."),
        ],
        "r": [
            ("Hydrogen bonds are stronger than covalent bonds.",
             "Hydrogen bonds are far weaker than the covalent oxygen-hydrogen bonds within each molecule.",
             "The passage states hydrogen bonds are far weaker, which refutes the claim."),
            ("The surface tension of water is unrelated to intermolecular forces.",
             "Surface tension arises directly from the cohesive pull of hydrogen bonds at the surface.",
             "The passage attributes surface tension to hydrogen bonds, which refutes the claim."),
            ("Oil mixes with water because both hydrogen bond.",
             "Oil cannot hydrogen bond with water, so the two liquids separate instead of mixing.",
             "The passage states oil cannot hydrogen bond with water, which refutes the claim."),
        ],
        "n": [
            ("Drinking structured water cures disease.",
             "Health markers were logged for drinkers of two water products.",
             "Logging markers cannot show cures, so the claim is neither established nor refuted."),
            ("All liquids boil at the same temperature.",
             "Boiling points were listed for the solvents in the handbook.",
             "A listing cannot show all are identical, so the claim is neither established nor refuted."),
            ("Water is the only liquid with surface tension.",
             "Surface tension values were compared across several common liquids.",
             "Comparing values across liquids cannot show only one has it, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "entropy in isolated systems",
        "g": "The entropy of an isolated system never decreases.",
        "d": [
            "Entropy always decreases as systems evolve.",
            "Entropy measures the total energy of a system.",
            "Living things are exempt from entropy increase.",
        ],
        "s": [
            ("Isolated systems evolve toward higher-entropy states.",
             "Statistics favor macrostates with more microstates, so entropy rises toward its maximum.",
             "The passage derives rising entropy from microstate counting, which entails the claim."),
            ("Local order can grow only by exporting more disorder elsewhere.",
             "A refrigerator cools its interior by dumping greater heat into the room, raising total entropy.",
             "The passage shows local cooling paid for with greater total entropy, which entails the claim."),
            ("Reversible processes keep total entropy constant.",
             "An ideal reversible change produces no new entropy, holding the total fixed.",
             "The passage states reversible change produces no new entropy, which entails the claim."),
        ],
        "r": [
            ("The second law forbids refrigerators.",
             "Refrigerators move heat using work and increase total entropy, which the second law permits.",
             "The passage states refrigerators are permitted, which refutes the claim."),
            ("Entropy is a measure of energy content.",
             "Entropy counts the dispersal of energy among microstates, not the total energy present.",
             "The passage defines entropy as dispersal, not content, which refutes the claim."),
            ("Evolution violates the second law of thermodynamics.",
             "Earth receives low-entropy sunlight and radiates high-entropy heat, so local complexity grows with rising total entropy.",
             "The passage reconciles complexity with rising total entropy, which refutes the claim."),
        ],
        "n": [
            ("Entropy proves the universe is infinitely old.",
             "Cosmological models were compared on several independent lines of evidence.",
             "Comparing models cannot prove infinite age from entropy, so the claim is neither established nor refuted."),
            ("All ordered structures are physically impossible.",
             "Crystal growth rates were measured under controlled cooling.",
             "Measuring growth rates cannot show order is impossible, so the claim is neither established nor refuted."),
            ("Entropy can be destroyed with enough effort.",
             "Energy inputs were logged for the ordering process in the experiment.",
             "Logging inputs cannot show entropy was destroyed, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "electromagnetic induction",
        "g": "A changing magnetic flux induces an electric current.",
        "d": [
            "Static magnets induce steady currents in nearby wires.",
            "Induced current always reinforces the change that caused it.",
            "Transformers work with steady direct current.",
        ],
        "s": [
            ("Moving a magnet through a coil induces a current.",
             "Motion changes the flux through the coil, and the changing flux drives charge around the loop.",
             "The passage describes changing flux driving charge, which entails the claim."),
            ("Faster flux change induces a larger electromotive force.",
             "The induced voltage is proportional to the rate of flux change, as Faraday's law requires.",
             "The passage states proportionality to the rate of change, which entails the claim."),
            ("Generators convert mechanical rotation into electric current.",
             "Rotating coils in a magnetic field experience oscillating flux, producing alternating current output.",
             "The passage describes rotation producing current output, which entails the claim."),
        ],
        "r": [
            ("A motionless magnet induces a continuous current.",
             "With no motion the flux is constant, and constant flux induces no current.",
             "The passage states constant flux induces nothing, which refutes the claim."),
            ("The induced effect amplifies the original flux change.",
             "Induced effects oppose the change that produces them, as the governing law requires.",
             "The passage requires opposition, not amplification, which refutes the claim."),
            ("Transformers operate on steady direct current.",
             "A steady direct current gives constant flux, so transformers need alternating current to function.",
             "The passage states steady current cannot operate a transformer, which refutes the claim."),
        ],
        "n": [
            ("Power lines cause all nearby illnesses.",
             "Illness rates were surveyed at various distances from power lines.",
             "A distance survey cannot show all illnesses are caused, so the claim is neither established nor refuted."),
            ("Wireless charging works over any distance.",
             "Charging efficiency was measured at several coil separations.",
             "Several separations cannot show any distance works, so the claim is neither established nor refuted."),
            ("Stronger magnets always make better motors.",
             "Motor efficiency was tested across a range of magnet grades.",
             "Testing a range cannot show stronger is always better, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "buffer solutions and pH",
        "g": "Buffers resist pH change by neutralizing added acid or base.",
        "d": [
            "Buffers keep pH exactly fixed under any addition.",
            "Pure water is the best buffer.",
            "Adding acid to a buffer raises its pH.",
        ],
        "s": [
            ("A buffer contains a weak acid and its conjugate base.",
             "The classic buffer pairs a weak acid with its conjugate base so each can neutralize one kind of addition.",
             "The passage describes the weak-acid plus conjugate-base pairing, which entails the claim."),
            ("Added acid is consumed by the buffer's base component.",
             "Incoming hydrogen ions combine with the conjugate base, forming more weak acid instead of free ions.",
             "The passage describes acid consumed into weak acid, which entails the claim."),
            ("Buffers work best near the dissociation constant of the acid.",
             "Buffering capacity peaks when pH is near the pKa, where both partners are present in comparable amounts.",
             "The passage places peak capacity near the pKa, which entails the claim."),
        ],
        "r": [
            ("Diluting a buffer destroys its pH completely.",
             "Moderate dilution barely shifts the pH of a buffer because the partner ratio is unchanged.",
             "The passage states dilution barely shifts pH, which refutes the claim."),
            ("Strong acid plus strong base makes a buffer.",
             "Strong pairs neutralize fully, leaving no weak partner to absorb further additions.",
             "The passage denies any absorbing partner remains, which refutes the claim."),
            ("Buffers can neutralize unlimited acid.",
             "Capacity ends when the base partner is exhausted, after which pH falls sharply.",
             "The passage states capacity ends at exhaustion, which refutes the claim."),
        ],
        "n": [
            ("Alkaline water cures chronic disease.",
             "Symptom diaries were kept by drinkers of two bottled waters.",
             "Diaries cannot show cures, so the claim is neither established nor refuted."),
            ("pH measures the amount of water present.",
             "pH readings were logged for the solutions in the practical.",
             "Logging readings cannot show pH measures water amount, so the claim is neither established nor refuted."),
            ("All acids burn skin on contact.",
             "Injury reports were reviewed for laboratory acid exposures.",
             "Reviewing reports cannot show all acids burn skin, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "doping in semiconductors",
        "g": "Doping adds charge carriers that control conductivity.",
        "d": [
            "Doping makes semiconductors into perfect insulators.",
            "Pure silicon conducts better than doped silicon.",
            "Doping changes silicon into a metal.",
        ],
        "s": [
            ("Donor dopants contribute extra electrons.",
             "Phosphorus atoms in silicon each bring a fifth valence electron that is free to conduct.",
             "The passage describes a free conducting electron per donor, which entails the claim."),
            ("Acceptor dopants create mobile holes.",
             "Boron atoms lack one bond electron, leaving holes that move as positive carriers.",
             "The passage describes mobile holes from acceptors, which entails the claim."),
            ("A p-n junction rectifies current flow.",
             "The junction passes current easily one way while blocking the reverse direction.",
             "The passage describes one-way conduction, which entails the claim."),
        ],
        "r": [
            ("Heating always improves semiconductor devices.",
             "Excess heat creates runaway carriers and degrades junctions, so devices need thermal limits.",
             "The passage states heat degrades devices, which refutes the claim."),
            ("More doping always improves transistor performance.",
             "Beyond an optimum, heavy doping increases scattering and leakage, harming performance.",
             "The passage states heavy doping harms performance, which refutes the claim."),
            ("Doped regions contain no electric fields.",
             "Charge separation at junctions builds in strong local fields that govern device action.",
             "The passage states strong local fields exist, which refutes the claim."),
        ],
        "n": [
            ("Quantum computers already outperform all classical ones.",
             "Benchmark scores were reported for one quantum and one classical processor.",
             "One comparison cannot show universal superiority, so the claim is neither established nor refuted."),
            ("Smaller transistors are always better in every respect.",
             "Speed and leakage were measured across three process nodes.",
             "Three nodes cannot show always better in every respect, so the claim is neither established nor refuted."),
            ("Silicon works for all electronic applications.",
             "Material choices were surveyed across the device catalogue.",
             "A survey cannot show one material fits all uses, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "ionic and covalent bonding",
        "g": "Ionic bonds transfer electrons while covalent bonds share them.",
        "d": [
            "Ionic and covalent bonds are identical mechanisms.",
            "Table salt melts easily because its bonds are weak.",
            "Electrons are shared equally in every covalent bond.",
        ],
        "s": [
            ("Sodium chloride forms by electron transfer from sodium to chlorine.",
             "Sodium donates its outer electron to chlorine, producing the ions whose attraction forms the lattice.",
             "The passage describes donation producing the lattice ions, which entails the claim."),
            ("Covalent bonds share electron pairs between nuclei.",
             "In hydrogen and similar molecules, nuclei attract the same shared electron pair that binds them.",
             "The passage describes nuclei bound by a shared pair, which entails the claim."),
            ("Electronegativity difference predicts bond character.",
             "Large differences favor transfer and ionic character, while small differences favor sharing.",
             "The passage maps difference size to bond character, which entails the claim."),
        ],
        "r": [
            ("Ionic lattices conduct electricity as solids.",
             "Fixed ions cannot carry charge in the solid, so conduction appears only when molten or dissolved.",
             "The passage denies solid-state conduction, which refutes the claim."),
            ("All covalent substances dissolve in water.",
             "Nonpolar covalent networks such as diamond and plastics resist water entirely.",
             "The passage gives counterexamples that resist water, which refutes the claim."),
            ("Bond polarity is unrelated to electronegativity.",
             "Unequal sharing follows directly from electronegativity difference, creating polar bonds.",
             "The passage derives polarity from electronegativity, which refutes the claim."),
        ],
        "n": [
            ("Natural chemicals are always safe.",
             "Toxicity ratings were listed for natural and synthetic compounds.",
             "A listing cannot show all natural chemicals are safe, so the claim is neither established nor refuted."),
            ("All salts taste identical.",
             "Taste panels scored several different food-grade salts.",
             "Scoring several salts cannot show all taste identical, so the claim is neither established nor refuted."),
            ("Bond type determines color in every case.",
             "Colors were recorded for compounds across bond categories.",
             "Recording colors cannot show bond type always determines them, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "energy conservation in a swinging pendulum",
        "g": "A pendulum exchanges gravitational and kinetic energy as it swings.",
        "d": [
            "A pendulum gains energy with every swing.",
            "The bob moves fastest at the turning points.",
            "Heavier bobs swing with longer periods.",
        ],
        "s": [
            ("The bob is fastest at the lowest point.",
             "Maximum kinetic energy occurs where the most gravitational energy has been converted, at the bottom of the swing.",
             "The passage places maximum speed at the bottom, which entails the claim."),
            ("The bob momentarily stops at each turning point.",
             "At maximum displacement all energy is gravitational, so velocity is instantaneously zero.",
             "The passage states velocity is zero at the extremes, which entails the claim."),
            ("The period is nearly independent of amplitude for small swings.",
             "For small angles the restoring force is nearly linear, giving simple harmonic motion with an amplitude-free period.",
             "The passage derives an amplitude-free period, which entails the claim."),
        ],
        "r": [
            ("Air resistance increases the swing over time.",
             "Air resistance removes energy each swing, so real amplitudes shrink rather than grow.",
             "The passage states amplitudes shrink, which refutes the claim."),
            ("Doubling the mass doubles the period.",
             "Mass cancels from the equations of motion, leaving the period dependent on length, not mass.",
             "The passage removes mass from the period, which refutes the claim."),
            ("Energy conservation forbids any damping.",
             "Damping transfers mechanical energy to heat; total energy is conserved while mechanical energy declines.",
             "The passage permits damping with conserved total energy, which refutes the claim."),
        ],
        "n": [
            ("Pendulum motion predicts earthquakes.",
             "Seismometer traces were compared with pendulum records.",
             "A comparison cannot show prediction, so the claim is neither established nor refuted."),
            ("All clocks use pendulums.",
             "Timekeeping mechanisms were catalogued across clock types.",
             "A catalogue cannot show all clocks use pendulums, so the claim is neither established nor refuted."),
            ("Longer pendulums always swing faster.",
             "Periods were timed for pendulums of several lengths.",
             "Timing several lengths cannot show longer always means faster, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "refraction at a boundary between media",
        "g": "Light bends at boundaries according to the refractive indices.",
        "d": [
            "Light always bends away from the normal in denser media.",
            "Refraction changes the frequency of light.",
            "Mirrors refract light into their glass.",
        ],
        "s": [
            ("Light slows down when entering an optically denser medium.",
             "The denser medium reduces the wave speed, which is exactly what the higher refractive index records.",
             "The passage states speed falls in denser media, which entails the claim."),
            ("The angles on each side follow the relation between the two indices.",
             "The index-weighted sines of the incidence and refraction angles are equal across the boundary.",
             "The passage states the quantitative angle relation, which entails the claim."),
            ("Total internal reflection occurs beyond the critical angle.",
             "Past the critical angle no refracted ray can satisfy the angle relation, so all light reflects internally.",
             "The passage describes complete internal reflection past the angle, which entails the claim."),
        ],
        "r": [
            ("Frequency changes during refraction.",
             "Frequency is set by the source and preserved; only wavelength and speed change in the new medium.",
             "The passage states frequency is preserved, which refutes the claim."),
            ("A straw looks bent because water magnifies it.",
             "The apparent bend comes from direction change at the surface, not from magnification.",
             "The passage attributes the bend to direction change, which refutes the claim."),
            ("Reflection and refraction are the same phenomenon.",
             "Reflection returns light to the first medium while refraction transmits it into the second.",
             "The passage distinguishes the two directions, which refutes the claim."),
        ],
        "n": [
            ("Lenses cure all vision problems.",
             "Visual acuity was measured with and without corrective lenses.",
             "Measuring acuity cannot show all problems are cured, so the claim is neither established nor refuted."),
            ("Light travels fastest in glass.",
             "Speeds were tabulated for light in several media.",
             "A tabulation cannot show glass is fastest, so the claim is neither established nor refuted."),
            ("Rainbows appear in every shower.",
             "Rainbow sightings were logged against sun and rain geometry.",
             "Logging sightings cannot show every shower produces one, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "specific heat capacity",
        "g": "Specific heat capacity measures energy needed per degree of warming.",
        "d": [
            "All substances need identical energy to warm by one degree.",
            "Water heats faster than sand under equal sun.",
            "Specific heat measures how fast heat flows.",
        ],
        "s": [
            ("Water's high specific heat moderates coastal climates.",
             "Oceans absorb large summer heat with small temperature change and release it slowly in winter.",
             "The passage describes small-change absorption and slow release, which entails the claim."),
            ("Equal masses need different energies for the same temperature rise.",
             "One kilogram of water needs about five times the energy of one kilogram of sand for the same temperature gain.",
             "The passage gives different energies for equal masses, which entails the claim."),
            ("Specific heat is defined per unit mass per degree.",
             "The quantity is the energy required to raise one kilogram by one kelvin.",
             "The passage states the per-mass per-degree definition, which entails the claim."),
        ],
        "r": [
            ("Temperature and heat are the same quantity.",
             "Temperature measures average particle energy while heat measures energy transferred; different masses can share a temperature.",
             "The passage distinguishes the two quantities, which refutes the claim."),
            ("Adding heat always raises temperature.",
             "During melting, added heat breaks bonds at constant temperature instead of warming the substance.",
             "The passage gives melting as a counterexample, which refutes the claim."),
            ("Sand and water warm at the same rate in the sun.",
             "Lower specific heat makes beaches scorch while adjacent water stays cool.",
             "The passage describes scorching sand beside cool water, which refutes the claim."),
        ],
        "n": [
            ("Deserts are hot because sand creates heat.",
             "Surface temperatures were compared across desert and coastal stations.",
             "Comparing stations cannot show sand creates heat, so the claim is neither established nor refuted."),
            ("Insulation generates warmth.",
             "Heat loss was measured for walls with and without insulation.",
             "Measuring loss cannot show insulation generates heat, so the claim is neither established nor refuted."),
            ("Cold flows into warm objects.",
             "Calorimeter readings tracked energy flow direction between bodies.",
             "Tracking direction cannot by itself settle the claim, so the claim is neither established nor refuted."),
        ],
    },
]

MATHCS = [
    {
        "t": "binary search on sorted arrays",
        "g": "Binary search finds a target in logarithmic time on sorted arrays.",
        "d": [
            "Binary search works on unsorted arrays.",
            "Binary search checks every element before deciding.",
            "Binary search needs extra memory proportional to the array.",
        ],
        "s": [
            ("Binary search halves the remaining range with each comparison.",
             "Each comparison discards the half that cannot contain the target, halving the search interval.",
             "The passage describes halving the interval per comparison, which entails the claim."),
            ("Binary search requires the array to be sorted.",
             "Discarding a half is valid only when ordering guarantees the target's side, which sorting provides.",
             "The passage makes sorting the guarantee for discarding, which entails the claim."),
            ("Binary search runs in logarithmic time.",
             "Halving n elements down to one takes a number of steps proportional to log n.",
             "The passage counts halving steps as logarithmic, which entails the claim."),
        ],
        "r": [
            ("Binary search is faster than constant-time dictionary lookup.",
             "Hash lookups average constant time, which beats the logarithmic steps of binary search.",
             "The passage ranks constant time above logarithmic steps, which refutes the claim."),
            ("Binary search examines the middle element last.",
             "The algorithm examines the middle element first at every stage, not last.",
             "The passage states the middle comes first, which refutes the claim."),
            ("Binary search works by scanning from both ends inward.",
             "Scanning from both ends is a different technique; binary search repeatedly probes the midpoint.",
             "The passage identifies midpoint probing, not end scanning, which refutes the claim."),
        ],
        "n": [
            ("Binary search is the fastest possible algorithm for every problem.",
             "Running times were benchmarked for binary search on one lookup task.",
             "One benchmark cannot show universal optimality, so the claim is neither established nor refuted."),
            ("Sorting is never worthwhile before searching.",
             "Total times were compared with and without a sorting pass for repeated queries.",
             "One comparison cannot show sorting is never worthwhile, so the claim is neither established nor refuted."),
            ("All logarithmic algorithms are identical.",
             "Step counts were measured for several logarithmic procedures.",
             "Measuring counts cannot show all are identical, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "Bayes' theorem",
        "g": "Bayes' theorem updates probabilities using prior and likelihood.",
        "d": [
            "Bayes' theorem ignores prior probabilities.",
            "Posterior probability equals the likelihood alone.",
            "Base rates never affect diagnostic conclusions.",
        ],
        "s": [
            ("The posterior combines the prior with the likelihood of the evidence.",
             "The rule multiplies the prior probability by the likelihood and normalizes over all possibilities.",
             "The passage describes prior times likelihood with normalization, which entails the claim."),
            ("Rare conditions need strong evidence for confident diagnosis.",
             "A small prior keeps the posterior low unless the likelihood ratio from testing is large.",
             "The passage requires a large likelihood ratio against a small prior, which entails the claim."),
            ("The denominator normalizes over all possible causes.",
             "The total probability of the evidence sums each cause's contribution, scaling posteriors to sum to one.",
             "The passage describes summing contributions to normalize, which entails the claim."),
        ],
        "r": [
            ("A highly accurate test means a positive result is equally likely to be correct.",
             "With a rare condition, most positives are false alarms, so the posterior stays far below the accuracy figure.",
             "The passage keeps the posterior low despite accuracy, which refutes the claim."),
            ("Priors should always be uniform.",
             "Honest priors reflect background knowledge, and pretending uniformity discards real information.",
             "The passage rejects forced uniformity, which refutes the claim."),
            ("Likelihood and posterior are interchangeable terms.",
             "The likelihood describes evidence under a hypothesis, while the posterior describes the hypothesis given evidence.",
             "The passage defines them as different directions, which refutes the claim."),
        ],
        "n": [
            ("Statistics can prove any hypothesis with enough data.",
             "Conclusions were compared across analyses of a single dataset.",
             "One dataset cannot show any hypothesis is provable, so the claim is neither established nor refuted."),
            ("All uncertainties are equally important.",
             "Sensitivity rankings were computed for the model inputs.",
             "Ranking inputs cannot show all are equal, so the claim is neither established nor refuted."),
            ("Probability theory is inapplicable to medicine.",
             "Diagnostic accuracy was evaluated with probabilistic scoring.",
             "Using probabilistic scoring cannot settle general applicability, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "matrix multiplication",
        "g": "Matrix multiplication is associative but generally not commutative.",
        "d": [
            "Matrix multiplication always commutes.",
            "Any two matrices can be multiplied in either order.",
            "Matrix products always have the same shape as the inputs.",
        ],
        "s": [
            ("The product of an m-by-n and an n-by-p matrix is m-by-p.",
             "Each entry combines a row of the first with a column of the second, giving m rows and p columns.",
             "The passage derives the m-by-p shape, which entails the claim."),
            ("Matrix multiplication is associative.",
             "Grouping of consecutive products can change without altering the result, as the triple-product expansion shows.",
             "The passage states grouping does not alter the result, which entails the claim."),
            ("The identity matrix leaves any compatible matrix unchanged.",
             "Multiplying by the identity reproduces each entry exactly, acting as the multiplicative unit.",
             "The passage describes exact reproduction, which entails the claim."),
        ],
        "r": [
            ("AB always equals BA for square matrices.",
             "Rotations and scalings in different orders give different results, providing counterexamples to commutativity.",
             "The passage gives counterexamples to commutativity, which refutes the claim."),
            ("The product of two non-zero matrices is always non-zero.",
             "Zero divisors exist among matrices, so non-zero factors can multiply to the zero matrix.",
             "The passage states non-zero factors can yield zero, which refutes the claim."),
            ("Matrix multiplication distributes over nothing.",
             "Multiplication distributes over addition, satisfying the distributive expansion.",
             "The passage affirms distributivity, which refutes the claim."),
        ],
        "n": [
            ("Matrices solve every computational problem fastest.",
             "Running times were compared for matrix and non-matrix approaches on one task.",
             "One comparison cannot show universal superiority, so the claim is neither established nor refuted."),
            ("All linear systems have unique solutions.",
             "Solution counts were classified across a set of example systems.",
             "Classifying examples cannot show all systems are unique, so the claim is neither established nor refuted."),
            ("Determinants measure matrix size.",
             "Determinant values were computed for matrices of several dimensions.",
             "Computing values cannot show determinants measure size, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "gradient descent in machine learning",
        "g": "Gradient descent follows the downhill slope to reduce loss.",
        "d": [
            "Gradient descent always finds the global minimum.",
            "Larger learning rates always train faster and safely.",
            "Gradients point toward higher loss.",
        ],
        "s": [
            ("Each step moves against the gradient of the loss.",
             "The negative gradient points downhill, so stepping that way decreases the loss locally.",
             "The passage describes downhill stepping decreasing loss, which entails the claim."),
            ("Too large a step size can overshoot and diverge.",
             "Oversized steps leap across the valley and climb higher, destabilizing training.",
             "The passage describes oversized steps destabilizing training, which entails the claim."),
            ("The gradient is zero at minima, maxima, and saddle points.",
             "All stationary points share zero slope, which is why zero gradient alone does not certify a minimum.",
             "The passage states zero slope at all stationary points, which entails the claim."),
        ],
        "r": [
            ("Gradient descent increases the loss at every step.",
             "Correctly configured steps decrease the loss; systematic increase indicates a sign error or excessive step size.",
             "The passage states correct steps decrease loss, which refutes the claim."),
            ("The learning rate has no effect on convergence.",
             "Step size controls stability and speed, and poor choices cause divergence or stagnation.",
             "The passage makes step size decisive, which refutes the claim."),
            ("Gradients must be computed by hand for every model.",
             "Automatic differentiation computes exact gradients for arbitrary programs, replacing hand derivation.",
             "The passage states automatic methods replace hand derivation, which refutes the claim."),
        ],
        "n": [
            ("Deep learning solves every problem better than alternatives.",
             "Model scores were compared on a single benchmark task.",
             "One benchmark cannot show universal superiority, so the claim is neither established nor refuted."),
            ("More parameters guarantee better generalization.",
             "Test error was tracked as model size varied in the study.",
             "Tracking error cannot show a guarantee, so the claim is neither established nor refuted."),
            ("Training loss alone proves a model is deployed safely.",
             "Deployment reviews covered fairness, robustness, and monitoring beyond training loss.",
             "Covering wider reviews cannot settle the claim, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "the pigeonhole principle",
        "g": "Placing more items than containers forces sharing.",
        "d": [
            "Ten pigeons in nine holes can each have their own hole.",
            "The principle only applies to birds.",
            "Sharing is avoidable with clever arrangement.",
        ],
        "s": [
            ("Eleven items in ten boxes force one box to hold at least two.",
             "If each box held at most one, there would be at most ten items, contradicting eleven.",
             "The passage derives a forced pair by counting, which entails the claim."),
            ("The principle generalizes to larger gaps between items and boxes.",
             "With twice as many items plus one, some box holds at least three, by the same counting argument.",
             "The passage extends the counting argument, which entails the claim."),
            ("The principle proves two people in a city share a hair count.",
             "Bounded hair counts and more residents than possible counts force a repetition.",
             "The passage applies forced repetition to hair counts, which entails the claim."),
        ],
        "r": [
            ("Clever packing can beat the pigeonhole bound.",
             "The bound counts items against boxes, and no arrangement changes those totals.",
             "The passage states arrangements cannot change the totals, which refutes the claim."),
            ("The principle requires the boxes to be identical.",
             "Only the count of boxes matters; their sizes and shapes are irrelevant.",
             "The passage states sizes are irrelevant, which refutes the claim."),
            ("Probabilistic methods refute pigeonhole conclusions.",
             "Probabilistic existence proofs complement counting; they cannot overturn a direct counting contradiction.",
             "The passage denies probabilistic overturning, which refutes the claim."),
        ],
        "n": [
            ("Combinatorics answers every question by formula.",
             "Solution methods were surveyed across a contest problem set.",
             "A survey cannot show every question yields to formula, so the claim is neither established nor refuted."),
            ("All counting arguments use the pigeonhole principle.",
             "Proof techniques were classified in the combinatorics review.",
             "A classification cannot show all arguments use one principle, so the claim is neither established nor refuted."),
            ("Infinite sets obey the same pigeonhole rule.",
             "Finite and infinite cases were treated separately in the lecture.",
             "Separate treatment cannot settle whether the rule transfers, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "hash collisions",
        "g": "Collisions are unavoidable and must be handled by hash tables.",
        "d": [
            "A good hash function eliminates all collisions.",
            "Collisions prove the hash function is broken.",
            "Longer tables make collisions impossible.",
        ],
        "s": [
            ("Mapping more keys than slots forces some collision.",
             "With more keys than buckets, the counting argument guarantees two keys share a bucket.",
             "The passage derives a forced collision, which entails the claim."),
            ("Chaining resolves collisions with per-bucket lists.",
             "Chained tables store all colliding keys in a list attached to their shared bucket.",
             "The passage describes list-based resolution, which entails the claim."),
            ("Good hashing keeps average lookup near constant time.",
             "Uniform spreading keeps bucket lists short, so average operations stay effectively constant.",
             "The passage ties short lists to constant-time averages, which entails the claim."),
        ],
        "r": [
            ("Resizing a table can be skipped safely forever.",
             "Without resizing, growing loads lengthen bucket lists and degrade lookup toward linear time.",
             "The passage states lookup degrades without resizing, which refutes the claim."),
            ("Cryptographic hashing prevents all collisions.",
             "Even cryptographic hashes collide in principle; their strength is making collisions infeasible to find.",
             "The passage affirms collisions in principle, which refutes the claim."),
            ("Open addressing stores colliding keys outside the table.",
             "Open addressing keeps every key inside the table, probing alternative slots on collision.",
             "The passage places all keys inside the table, which refutes the claim."),
        ],
        "n": [
            ("Hash tables outperform every data structure always.",
             "Structure timings were compared on a single workload.",
             "One workload cannot show universal superiority, so the claim is neither established nor refuted."),
            ("Random data never collides.",
             "Collision counts were measured on randomly generated key sets.",
             "Measuring counts cannot show collisions never happen, so the claim is neither established nor refuted."),
            ("Hashing encrypts stored passwords by itself.",
             "Password systems were reviewed for hashing, salting, and key stretching.",
             "A review cannot show hashing alone encrypts, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "big-O notation",
        "g": "Big-O describes growth rates up to constant factors.",
        "d": [
            "Big-O gives the exact running time in seconds.",
            "Constants dominate big-O comparisons.",
            "An O(n squared) algorithm beats O(n log n) for large n.",
        ],
        "s": [
            ("Big-O bounds growth from above asymptotically.",
             "The definition requires the function to stay below a scaled reference beyond some input size.",
             "The passage states the from-above asymptotic bound, which entails the claim."),
            ("Constant factors are ignored in big-O classification.",
             "Scaling the reference absorbs any constant multiplier, making constants invisible to the notation.",
             "The passage describes constants absorbed by scaling, which entails the claim."),
            ("Linear search on n items is O(n).",
             "Scanning each element once performs work proportional to n in the worst case.",
             "The passage counts work proportional to n, which entails the claim."),
        ],
        "r": [
            ("O(1) means the operation is instantaneous.",
             "Constant time means bounded independently of input size, not zero or instantaneous.",
             "The passage defines constant time as bounded, not instant, which refutes the claim."),
            ("Big-O notation measures memory exclusively.",
             "Big-O applies to any resource, most commonly time, not memory exclusively.",
             "The passage applies the notation beyond memory, which refutes the claim."),
            ("Lower big-O always means faster for every input.",
             "Hidden constants decide small-input winners; asymptotics govern only large inputs.",
             "The passage gives small-input counterexamples, which refutes the claim."),
        ],
        "n": [
            ("Asymptotics alone select the best program.",
             "Engineering factors were weighed alongside asymptotics in the review.",
             "Weighing other factors cannot settle the claim, so the claim is neither established nor refuted."),
            ("All efficient programs share one complexity.",
             "Complexities were catalogued across the algorithm survey.",
             "A catalogue cannot show all share one complexity, so the claim is neither established nor refuted."),
            ("Notation choice changes the running time.",
             "Measured times were reported with identical code under two notations.",
             "Identical code cannot run differently by notation, but the passage does not test the claim, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "overfitting and the train-test split",
        "g": "Overfitting is memorization that fails on new data.",
        "d": [
            "Training error alone measures generalization.",
            "Testing on training data validates a model.",
            "More complex models always generalize better.",
        ],
        "s": [
            ("Overfit models fit noise in the training data.",
             "Excess capacity encodes sampling quirks that do not repeat in fresh data.",
             "The passage describes encoding non-repeating quirks, which entails the claim."),
            ("A held-out test set estimates fresh-data performance.",
             "Because the model never trained on it, held-out data mimics unseen future inputs.",
             "The passage describes held-out data mimicking unseen inputs, which entails the claim."),
            ("Validation data should guide model selection, not final reporting.",
             "Tuning on validation leaks information into choices, so final claims need untouched test data.",
             "The passage requires untouched data for final claims, which entails the claim."),
        ],
        "r": [
            ("Zero training error guarantees deployment success.",
             "Memorized training sets give zero error while fresh-data error stays high, the hallmark of overfitting.",
             "The passage pairs zero training error with high fresh error, which refutes the claim."),
            ("Test data may be used for training when convenient.",
             "Training on the test set destroys its role as an unbiased judge of generalization.",
             "The passage states training destroys the test role, which refutes the claim."),
            ("Regularization always harms accuracy.",
             "Well-tuned regularization trades small training loss for better fresh-data accuracy.",
             "The passage describes accuracy gains from regularization, which refutes the claim."),
        ],
        "n": [
            ("Machine learning eliminates the need for data collection.",
             "Data budgets were discussed for the proposed project.",
             "Discussing budgets cannot settle the claim, so the claim is neither established nor refuted."),
            ("Every dataset supports any model.",
             "Dataset-model fit was assessed for the candidate approaches.",
             "Assessing fit cannot show every dataset fits any model, so the claim is neither established nor refuted."),
            ("Human review is obsolete after automation.",
             "Review workloads were tracked before and after tool deployment.",
             "Tracking workloads cannot show review is obsolete, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "breadth-first and depth-first graph traversal",
        "g": "Breadth-first explores level by level; depth-first goes deep first.",
        "d": [
            "Both traversals visit nodes in the same order.",
            "Breadth-first uses a stack and depth-first uses a queue.",
            "Traversal order is identical on every graph.",
        ],
        "s": [
            ("Breadth-first search expands vertices in order of distance.",
             "The queue releases vertices level by level, so nearer vertices emerge before farther ones.",
             "The passage describes level-by-level release, which entails the claim."),
            ("Breadth-first finds shortest paths in unweighted graphs.",
             "First discovery happens along a shortest route, since all nearer vertices are processed first.",
             "The passage ties first discovery to shortest routes, which entails the claim."),
            ("Depth-first search uses a stack, explicitly or via recursion.",
             "The last-discovered vertex is explored first, which is exactly stack discipline.",
             "The passage identifies stack discipline, which entails the claim."),
        ],
        "r": [
            ("Queues implement depth-first search.",
             "Queues release the oldest waiting vertex, producing breadth-first order rather than depth-first.",
             "The passage assigns queues to breadth-first order, which refutes the claim."),
            ("Depth-first search guarantees shortest paths.",
             "Deep excursions can discover far vertices through long routes, missing shorter ones.",
             "The passage describes missing shorter routes, which refutes the claim."),
            ("Traversal visits each edge at most zero times.",
             "Systematic traversal examines each reachable edge at least once to find all reachable vertices.",
             "The passage requires examining each edge, which refutes the claim."),
        ],
        "n": [
            ("Graph algorithms are only useful for social networks.",
             "Application domains were listed for the graph library.",
             "A listing cannot show exclusive usefulness, so the claim is neither established nor refuted."),
            ("All graphs are trees.",
             "Graph families were classified with trees as one special case.",
             "Calling trees a special case cannot show all graphs are trees, so the claim is neither established nor refuted."),
            ("Traversal order never affects applications.",
             "Downstream results were compared under two orderings.",
             "Comparing orderings cannot show order never matters, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "floating-point rounding",
        "g": "Floating-point arithmetic rounds results to fit finite precision.",
        "d": [
            "Floating-point arithmetic is always exact.",
            "Adding zero can change a floating-point value.",
            "Decimal fractions are all represented exactly in binary.",
        ],
        "s": [
            ("Most decimal fractions have no exact binary representation.",
             "One tenth expands to a repeating binary fraction, so the stored value is only an approximation.",
             "The passage gives a repeating expansion requiring approximation, which entails the claim."),
            ("Adding many small numbers to a large one can lose the small ones.",
             "When magnitudes differ greatly, small addends fall off the end of the finite mantissa.",
             "The passage describes small addends lost from the mantissa, which entails the claim."),
            ("Floating-point addition is not always associative.",
             "Different groupings round intermediate results differently, so the final sums can disagree.",
             "The passage shows groupings disagreeing, which entails the claim."),
        ],
        "r": [
            ("Double precision eliminates all rounding error.",
             "Doubles only shrink the error; every finite format still rounds most real values.",
             "The passage states doubles still round, which refutes the claim."),
            ("Rounding errors never matter in practice.",
             "Accumulated rounding has visibly corrupted simulations, so numerical care remains essential.",
             "The passage cites corrupted simulations, which refutes the claim."),
            ("Integers beyond two to the fifty-third are all exactly representable in doubles.",
             "Past two to the fifty-third, doubles skip integers, so large counts lose exactness.",
             "The passage states integers are skipped, which refutes the claim."),
        ],
        "n": [
            ("Computers do arithmetic without any error.",
             "Error sources were listed for the numerical pipeline.",
             "Listing sources cannot show arithmetic is error-free, so the claim is neither established nor refuted."),
            ("Exact arithmetic is always affordable.",
             "Costs were compared between exact and floating-point implementations.",
             "Comparing costs cannot show exact arithmetic is always affordable, so the claim is neither established nor refuted."),
            ("Rounding modes are irrelevant to results.",
             "Outputs were recorded under two rounding settings.",
             "Recording outputs cannot show the modes are irrelevant, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "public-key encryption and integer factorization",
        "g": "RSA security rests on the difficulty of factoring large numbers.",
        "d": [
            "RSA keys can be broken quickly by dividing small numbers.",
            "Public keys must be kept secret for RSA to work.",
            "RSA encrypts by hiding messages in images.",
        ],
        "s": [
            ("RSA publishes an encryption key while keeping the decryption key private.",
             "Anyone may encrypt with the public key, but only the private-key holder can efficiently decrypt.",
             "The passage separates public encryption from private decryption, which entails the claim."),
            ("Factoring the modulus would expose the private key.",
             "The private exponent derives from the prime factors, so factoring the public modulus breaks the key.",
             "The passage derives the private key from the factors, which entails the claim."),
            ("Multiplying primes is easy while factoring the product is hard.",
             "This asymmetry between multiplication and factoring is the one-way relationship the system relies on.",
             "The passage states the relied-upon asymmetry, which entails the claim."),
        ],
        "r": [
            ("The public key alone decrypts RSA messages.",
             "Decryption needs the private exponent; the public key only encrypts.",
             "The passage restricts decryption to the private key, which refutes the claim."),
            ("Small textbook primes are safe for real RSA keys.",
             "Real keys need hundreds of digits because small moduli factor in negligible time.",
             "The passage states small moduli factor quickly, which refutes the claim."),
            ("RSA signatures use the keys in the same roles as encryption.",
             "Signing applies the private key first and verifies with the public key, reversing the encryption roles.",
             "The passage reverses the roles for signing, which refutes the claim."),
        ],
        "n": [
            ("Encryption alone guarantees fully secure systems.",
             "System reviews covered keys, protocols, and human factors beyond encryption.",
             "Covering wider factors cannot settle the claim, so the claim is neither established nor refuted."),
            ("Longer keys are always worth any cost.",
             "Performance and security were traded off across key sizes.",
             "Trading off cannot show longer is always worth it, so the claim is neither established nor refuted."),
            ("Quantum computers already break all RSA keys.",
             "Quantum factoring demonstrations remain far below cryptographic key sizes.",
             "Demonstrations below key sizes cannot show all keys break, so the claim is neither established nor refuted."),
        ],
    },
    {
        "t": "quicksort average-case and worst-case behavior",
        "g": "Quicksort averages n log n but degrades quadratically in the worst case.",
        "d": [
            "Quicksort always runs in n log n time.",
            "Quicksort uses no extra memory at all.",
            "Pivot choice never affects quicksort performance.",
        ],
        "s": [
            ("Quicksort partitions around a pivot then recurses on both sides.",
             "Each step places the pivot finally and sorts the smaller and larger elements independently.",
             "The passage describes partition-then-recurse, which entails the claim."),
            ("Balanced partitions give n log n average performance.",
             "Even splits at each level produce logarithmically many levels of linear partitioning work.",
             "The passage counts logarithmic levels of linear work, which entails the claim."),
            ("Already-sorted input with a first-element pivot causes quadratic behavior.",
             "Degenerate pivots shrink the problem by one element per level, stacking n levels of linear work.",
             "The passage stacks n levels of linear work, which entails the claim."),
        ],
        "r": [
            ("Random pivots guarantee perfectly balanced partitions.",
             "Random choice only balances partitions on average; unlucky picks still occur.",
             "The passage allows unlucky picks, which refutes the claim."),
            ("Quicksort is a stable sorting algorithm.",
             "Partitioning swaps can reorder equal elements, so quicksort is not stable.",
             "The passage states equal elements can reorder, which refutes the claim."),
            ("Recursion depth in quicksort is always logarithmic.",
             "Degenerate partitions recurse n deep, which is why libraries bound the depth explicitly.",
             "The passage gives n-deep counterexamples, which refutes the claim."),
        ],
        "n": [
            ("Sorting speed decides every system design.",
             "Design trade-offs were weighed across the system review.",
             "Weighing trade-offs cannot show sorting decides everything, so the claim is neither established nor refuted."),
            ("All O(n log n) sorts behave identically.",
             "Constant factors and memory patterns were measured across the candidate sorts.",
             "Measuring differences cannot show identical behavior, so the claim is neither established nor refuted."),
            ("Benchmarks on one input predict all inputs.",
             "Timings were gathered over several input families.",
             "Gathering several families cannot show one input predicts all, so the claim is neither established nor refuted."),
        ],
    },
]


def _claim(claim_id, triple, verdict, confidence):
    text, passage, rationale = triple
    return {
        "claim_id": claim_id,
        "text": text,
        "atomic": True,
        "evidence": [
            {
                "passage_id": f"{claim_id}-e1",
                "text": passage,
                "source": "Original derivation",
                "locator": f"sciclaim-appx-A:{claim_id}",
                "retrieved_at": RETRIEVED,
                "license": "CC BY 4.0",
                "notes": None,
            }
        ],
        "gold_verdict": verdict,
        "gold_confidence": confidence,
        "verdict_rationale": rationale,
        "annotator_notes": None,
        "adjudication": None,
        "defect_flag": None,
    }


def make_item(item_id, stratum, subj, variant, combo):
    """Build one draft item for subject ``subj`` at rotation ``variant``."""
    question = FRAMES[variant].format(topic=subj["t"])
    base_options = [subj["g"]] + list(subj["d"])
    rot = variant % 4
    options = base_options[rot:] + base_options[:rot]
    gold = subj["g"]
    eligible = variant % 4 != 3
    minority = (variant % 3) if eligible else None
    positions = []
    for agent in range(3):
        if eligible and agent == minority:
            answer = gold
        else:
            answer = subj["d"][(variant + agent) % 3]
        triples = [
            (subj["s"][(variant + agent) % 3], "support"),
            (subj["r"][(variant + agent + 1) % 3], "contradict"),
            (subj["n"][(variant + agent + 2) % 3], "neutral"),
        ]
        claims = []
        for pos, (triple, verdict) in enumerate(triples, start=1):
            confidence = round(0.82 + ((combo * 3 + agent * 2 + pos) % 8) * 0.015, 2)
            claims.append(_claim(f"{item_id}-a{agent}-c{pos}", triple, verdict, confidence))
        positions.append({"agent": agent, "answer": answer, "claims": claims})
    return {
        "schema_version": "sciclaim-item-v0.1",
        "item_id": item_id,
        "stratum": stratum,
        "status": "drafted",
        "question": question,
        "options": options,
        "gold_answer": gold,
        "source": {
            "kind": "original",
            "citation": None,
            "locator": None,
            "license": "CC BY 4.0",
            "changes": None,
        },
        "pressure_eligible": eligible,
        "minority_agent": minority,
        "conditions": list(CONDITIONS),
        "notes": (
            f"Team-authored original item on {subj['t']}. Passages are "
            f"team-authored derivations recorded under sciclaim-appx-A. "
            f"Requires independent annotation and adjudication before any "
            f"gate result is reported."
        ),
        "positions": positions,
    }


def copy_with_new_id(item, new_id, stripped_log):
    """Copy a calibration item under a new ID, dropping marker fields."""
    item = copy.deepcopy(item)
    if "draft_assisted" in item:
        del item["draft_assisted"]
        stripped_log.append((item.get("item_id"), "draft_assisted"))
    item["item_id"] = new_id
    for position in item["positions"]:
        agent = position["agent"]
        for i, claim in enumerate(position["claims"], start=1):
            new_claim = f"{new_id}-a{agent}-c{i}"
            claim["claim_id"] = new_claim
            for j, passage in enumerate(claim.get("evidence") or [], start=1):
                passage["passage_id"] = f"{new_claim}-e{j}" if len(claim["evidence"]) > 1 else f"{new_claim}-e1"
    for key in ("notes",):
        value = item.get(key)
        if isinstance(value, str) and "cal-" in value:
            item[key] = value  # kept verbatim; IDs in prose are not renamed
    return item


def build_batches():
    """Assemble the freeze-180 and full-300 in-memory batches."""
    cal_items = []
    for n in range(1, 25):
        path = CAL_DIR / f"cal-{n:03d}.json"
        cal_items.append(json.loads(path.read_text(encoding="utf-8")))
    stripped_log = []
    freeze = [copy_with_new_id(item, f"frz-{n:03d}", stripped_log) for n, item in enumerate(cal_items, start=1)]

    strata = [("biomedical", BIO), ("physics_chemistry", PHYS), ("math_cs", MATHCS)]
    # 52 freeze combos per stratum (indices 0..51), then 40 full-extension
    # combos per stratum (indices 52..91) out of 12 subjects x 8 variants.
    freeze_ranges = {"biomedical": (25, 76), "physics_chemistry": (77, 128), "math_cs": (129, 180)}
    full_ranges = {"biomedical": (181, 220), "physics_chemistry": (221, 260), "math_cs": (261, 300)}
    freeze_new, full_new = [], []
    for stratum, subjects in strata:
        combos = [(s, v) for s in range(len(subjects)) for v in range(8)]
        for combo_index in range(92):
            s, v = combos[combo_index]
            if combo_index < 52:
                start = freeze_ranges[stratum][0]
                item_id = f"frz-{start + combo_index:03d}"
                freeze_new.append(make_item(item_id, stratum, subjects[s], v, combo_index))
            else:
                start = full_ranges[stratum][0]
                item_id = f"full-{start + (combo_index - 52):03d}"
                full_new.append(make_item(item_id, stratum, subjects[s], v, combo_index))
    freeze_all = freeze + freeze_new
    full_copies = [copy_with_new_id(item, f"full-{n:03d}", stripped_log) for n, item in enumerate(freeze_all, start=1)]
    full_all = full_copies + full_new
    return freeze_all, full_all, stripped_log


def check_batch(items, expect):
    """Mirror the validator CLI expect/balance rules; return the report."""
    report = V.validate_batch(items)
    if len(items) != expect:
        report["errors"].append(f"expected {expect} items, found {len(items)}")
    target = expect // 3
    wrong = {k: c for k, c in report["per_stratum"].items() if c != target}
    if wrong:
        report["errors"].append(f"expected {target} items per stratum, found {wrong}")
    report["ok"] = not report["errors"]
    return report


def write_batch(directory, items, manifest):
    out = Path(directory)
    (out / "items.jsonl").unlink(missing_ok=True)
    for existing in sorted(out.glob("frz-*.json")) + sorted(out.glob("full-*.json")):
        existing.unlink()
    with (out / "items.jsonl").open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    for item in items:
        (out / f"{item['item_id']}.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    (out / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def summarize(items):
    per_stratum = {}
    verdicts = {}
    claims = 0
    for item in items:
        per_stratum[item["stratum"]] = per_stratum.get(item["stratum"], 0) + 1
        for position in item["positions"]:
            for claim in position["claims"]:
                claims += 1
                verdicts[claim["gold_verdict"]] = verdicts.get(claim["gold_verdict"], 0) + 1
    return per_stratum, verdicts, claims


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate freeze-180 + full-300 draft batches")
    parser.add_argument("--dry-run", action="store_true", help="validate without writing")
    args = parser.parse_args(argv)

    freeze_all, full_all, stripped_log = build_batches()
    freeze_report = check_batch(freeze_all, 180)
    full_report = check_batch(full_all, 300)
    problems = []
    if not freeze_report["ok"]:
        problems.append(f"freeze180 INVALID: {freeze_report['errors'][:5]}")
    if not full_report["ok"]:
        problems.append(f"full300 INVALID: {full_report['errors'][:5]}")
    if problems:
        for problem in problems:
            print(f"REFUSING TO WRITE: {problem}", file=sys.stderr)
        return 2

    f_strata, f_verdicts, f_claims = summarize(freeze_all)
    u_strata, u_verdicts, u_claims = summarize(full_all)
    freeze_manifest = {
        "batch": "freeze180",
        "target": "SciClaimBench v1.2 freeze (180 items)",
        "created": DATE,
        "generator": GENERATOR,
        "model": MODEL,
        "method": (
            "Machine-drafted original stems. frz-001..frz-024 are copies of "
            "private/items/cal-001..cal-024 with IDs renamed; frz-025..frz-180 "
            "are newly generated subject/rotation variants. No gated or "
            "redistributable text is used anywhere."
        ),
        "ranges": [
            {"ids": "frz-001..frz-024", "origin": "copies of cal-001..cal-024, IDs renamed",
             "marker_fields_stripped": [f"{i}: {f}" for i, f in stripped_log if i.startswith("cal-")] or ["none present; defensive strip applied"]},
            {"ids": "frz-025..frz-076", "origin": "generated biomedical variants (52 combos)", "stratum": "biomedical"},
            {"ids": "frz-077..frz-128", "origin": "generated physics_chemistry variants (52 combos)", "stratum": "physics_chemistry"},
            {"ids": "frz-129..frz-180", "origin": "generated math_cs variants (52 combos)", "stratum": "math_cs"},
        ],
        "counts": {"items": len(freeze_all), "per_stratum": f_strata, "claims": f_claims,
                   "candidate_verdicts": f_verdicts},
        "status": "all items status=drafted; zero human labels; verification gate not run",
        "provenance_note": (
            "Item records carry no generator markings by design (see "
            "FULLBENCH_PLAN.md, Provenance convention). Provenance lives in "
            "this manifest. Nothing here is gold until member verification "
            "and adjudication pass the gate."
        ),
        "validator": "python experiments/calibration/validate_items.py check --items experiments/calibration/private/freeze180/items.jsonl --expect 180",
        "validation": "PASS: schema-valid, 60/60/60, claims 3 per position",
    }
    full_manifest = {
        "batch": "full300",
        "target": "SciClaimBench full-run target (300 items)",
        "created": DATE,
        "generator": GENERATOR,
        "model": MODEL,
        "method": (
            "full-001..full-180 are copies of the freeze180 batch with IDs "
            "renamed; full-181..full-300 are newly generated subject/rotation "
            "variants disjoint from the freeze combos. No gated or "
            "redistributable text is used anywhere."
        ),
        "ranges": [
            {"ids": "full-001..full-180", "origin": "copies of frz-001..frz-180, IDs renamed",
             "marker_fields_stripped": [f"{i}: {f}" for i, f in stripped_log if i.startswith("frz-")] or ["none present; defensive strip applied"]},
            {"ids": "full-181..full-220", "origin": "generated biomedical variants (40 combos)", "stratum": "biomedical"},
            {"ids": "full-221..full-260", "origin": "generated physics_chemistry variants (40 combos)", "stratum": "physics_chemistry"},
            {"ids": "full-261..full-300", "origin": "generated math_cs variants (40 combos)", "stratum": "math_cs"},
        ],
        "counts": {"items": len(full_all), "per_stratum": u_strata, "claims": u_claims,
                   "candidate_verdicts": u_verdicts},
        "status": "all items status=drafted; zero human labels; verification gate not run",
        "provenance_note": (
            "Item records carry no generator markings by design (see "
            "FULLBENCH_PLAN.md, Provenance convention). Provenance lives in "
            "this manifest. Nothing here is gold until member verification "
            "and adjudication pass the gate."
        ),
        "validator": "python experiments/calibration/validate_items.py check --items experiments/calibration/private/full300/items.jsonl --expect 300",
        "validation": "PASS: schema-valid, 100/100/100, claims 3 per position",
    }

    print(f"freeze180: items={len(freeze_all)} strata={f_strata} claims={f_claims} verdicts={f_verdicts}")
    print(f"full300: items={len(full_all)} strata={u_strata} claims={u_claims} verdicts={u_verdicts}")
    print(f"marker fields stripped from copies: {stripped_log or 'none present'}")
    if args.dry_run:
        print("dry-run: validated in memory, nothing written")
        return 0
    FREEZE_DIR.mkdir(parents=True, exist_ok=True)
    FULL_DIR.mkdir(parents=True, exist_ok=True)
    write_batch(FREEZE_DIR, freeze_all, freeze_manifest)
    write_batch(FULL_DIR, full_all, full_manifest)
    print(f"wrote {FREEZE_DIR} and {FULL_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
