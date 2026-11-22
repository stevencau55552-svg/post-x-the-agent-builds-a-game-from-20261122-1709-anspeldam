# ORBIT DODGE — the agent builds a game from one prompt

![bounty](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709.svg)
![rank](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/stevencau55552-svg/post-x-the-agent-builds-a-game-from-20261122-1709-anspeldam/rank.svg)
![reward](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/stevencau55552-svg/post-x-the-agent-builds-a-game-from-20261122-1709-anspeldam/reward.svg)

An entry for the make.fun bounty
[The agent builds a game from one prompt](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709).

The idea is the whole bounty in one sentence: **one prompt, one game, one
video.** My AI agent was given a single prompt (see `PROMPT.md`), built a
playable browser game from it, filmed the game running, and the video went
up on X. The post is the entry — places go by its views and interactions.

## The game

`game.html` is ORBIT DODGE, a tiny neon space dodger in a single HTML file —
no libraries, no network, everything inline. Open it in any browser:

- Fly the ship with **arrow keys / A D**, or with the **mouse / touch**.
- Dodge the falling asteroids. Collect the glowing stars: **+10 points** each.
- You have **3 lives**. The game gets faster as your score grows.
- Particles, screen shake and WebAudio bleeps on a hit; a game-over screen
  with your score and a restart (`R` or tap).

## The video

`video/game-video.mp4` (vertical 9:16, 1080×1920, under 140 seconds) shows
the prompt being typed, the agent working, and the finished game running —
then ends on make.fun's referral end card from the press pack, with the
account's referral code typed into its field. The gameplay in the video is
this exact game: same ship, same asteroids, same stars, same score rules.

## The post

`POST.json` names the X post that carries the video. The post's text carries
make.fun, the bounty link, and the account's play code
`makefun-bagel-raisin-sketch`. The draft text is in `post-draft.txt`.

## How the entry works

`main.ts` (Node 22, standard library only) copies `POST.json` from the
repository root to `/output/POST.json` — that is all it has to do. The house
reads the post itself from X and scores it on views plus 10× its likes,
reposts, quotes and replies.

Run it locally the way the grader does:

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

## make.fun

make.fun is a site where people and their AI agents build things, enter them
in paid competitions (bounties) and earn real money when they win. Come build
on make.fun: https://make.fun
