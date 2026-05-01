# GPT Image 2 Pipeline Figure Prompt

This prompt is for a first-page overview figure that explains the entire study at a glance. It is meant to be pasted directly into GPT Image 2.

Recommended settings:

- Model: `gpt-image-2`
- Quality: `high`
- Size: `2560x1440` for a polished 16:9 report figure, or `1536x864` for a faster draft
- Output format: PNG

## Prompt

Create a single first-page executive overview figure for a Korean research report.

Use case: professional research-report infographic and workflow diagram.

Asset type: landscape 16:9 opening figure for a Word report.

Subject: a wartime reserve-force transportation simulation that compares bus-only transport against rail-bus multimodal transport. The figure should explain the full study pipeline in one glance, from input assumptions to transport alternatives, uncertainty, simulation, evaluation, and decision interpretation.

Visual style: clean flat editorial infographic, polished government/research-report style, white background, restrained colors, no photorealism, no stock-photo feeling, no decorative clutter. Use the same visual tone as a senior-level briefing slide: clear hierarchy, quiet confidence, high readability.

Color palette:

- navy for bus-only and road-related elements
- muted green for rail-bus multimodal and rail-related elements
- light gray for neutral process blocks
- subtle red only for risk or disruption markers
- dark charcoal for text

Canvas and layout:

- Use a wide left-to-right pipeline.
- Keep generous white space and balanced margins.
- Divide the figure into six clearly separated stages connected by arrows.
- In the middle, show two parallel comparison lanes: one for bus-only and one for rail-bus multimodal.
- Keep all icons simple and consistent: bus, road, train, route arrow, clock, warning marker, people group, destination marker, evaluation dashboard.
- Make every label large enough to read in a printed report.

Title at the top, exact text:

"전시 예비군 수송체계 시뮬레이션 개념도"

Required stage labels, exact Korean text only:

1. "상황 입력"
2. "수송 대안"
3. "불확실성"
4. "반복 시뮬레이션"
5. "평가 지표"
6. "의사결정 해석"

Inside "상황 입력", include only these short labels:

- "인원 규모"
- "출발지"
- "목적지"
- "수송 자원"

Inside "수송 대안", show two horizontal lanes with these exact labels:

- "버스 단독"
- "철도-버스 복합"

For "버스 단독", show a simple road route from origin to destination using bus icons.

For "철도-버스 복합", show bus to rail, rail segment, then bus to destination.

Inside "불확실성", include only these labels:

- "집결 지연"
- "도로 혼잡"
- "도로 장애"
- "환승 시간"

Inside "평가 지표", include only these labels:

- "완료시간"
- "미도착 인원"
- "자원 효율"

Inside "의사결정 해석", include only these labels:

- "신속성"
- "안정성"
- "자원 효율"

Composition details:

- Make the "수송 대안" section visually central and slightly larger than the other stages.
- Put "불확실성" as a slim band below the transport alternatives, feeding into "반복 시뮬레이션".
- Put "평가 지표" and "의사결정 해석" on the right side as the final output.
- Use arrows to show the flow: inputs -> alternatives plus uncertainty -> simulation -> metrics -> interpretation.
- The visual should feel like a complete research methodology diagram, not a marketing graphic.

Text constraints:

- Use only the Korean text explicitly listed above.
- Do not add any extra words, letters, numbers, captions, acronyms, legends, or footnotes.
- Spell all Korean labels exactly as written.
- Use crisp, high-contrast Korean typography.
- Avoid tiny text.
- Avoid overlapping text.

Safety and content constraints:

- No soldiers.
- No weapons.
- No explosions.
- No flags.
- No real-world map.
- No official seals or logos.
- No classified-document styling.
- No watermark.

Quality requirements:

- The figure must be understandable within five seconds.
- It should look appropriate for the first page of a formal Korean defense-logistics research report.
- It should prioritize clarity, hierarchy, and readability over decoration.
- The final image should have clean edges, aligned blocks, consistent icon style, and enough white space for Word document insertion.

## Applied Prompting Guidance

This prompt follows the official GPT Image prompting guide by specifying the artifact type, intended use, layout hierarchy, exact text, visual language, and constraints. It also uses a landscape slide-style canvas and `high` quality because the figure contains structured labels and dense diagram content.

References:

- https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
- https://developers.openai.com/api/docs/models/gpt-image-2
