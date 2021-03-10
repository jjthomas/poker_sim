import sys
import random
import time

SF = 0
Q = 1
FH = 2
F = 3
S = 4
T = 5
TP = 6
P = 7
H = 8

names = ["straight flush", "quads", "full house", "flush",
"straight", "trips", "two pair", "pair", "high card"]

def dup_ace(hand):
  new_hand = hand[:]
  for c in hand:
    if c[0] == 12: # ace
      new_hand.insert(0, (-1, c[1]))
  return new_hand

def check_sf(hand):
  hand = sorted(dup_ace(hand), key=lambda x: (x[1], x[0]))
  for i in range(len(hand) - 1, 3, -1):
    success = True
    for j in range(i - 1, i - 5, -1):
      if hand[j][0] != hand[j + 1][0] - 1 or hand[j][1] != hand[j + 1][1]:
        success = False
        break
    if success:
      return (SF, [hand[i]])
  return None

def check_q(hand):
  for i in range(len(hand) - 1, 2, -1):
    success = True
    for j in range(i - 1, i - 4, -1):
      if hand[j][0] != hand[j + 1][0]:
        success = False
        break
    if success:
      return (Q, [hand[i], hand[i - 4] if i == 6 else hand[i + 1]])
  return None

def check_fh(hand):
  trip = None
  pair = None
  idx = len(hand) - 2
  count = 0
  while idx >= -1: # final iteration -1
    if idx == -1 or hand[idx][0] != hand[idx + 1][0]:
      if count == 1 and pair is None:
        pair = hand[idx + 1]
      elif count == 2:
        if trip is None:
          trip = hand[idx + 1]
        else:
          pair = hand[idx + 1]
      count = 0
    else:
      count += 1
    idx -= 1
  return None if pair is None or trip is None else (FH, [trip, pair])

def elim_dups(hand):
  new_hand = hand[:]
  for i in range(len(hand) - 2, -1, -1):
    if hand[i][0] == hand[i + 1][0]:
      del new_hand[i]
  return new_hand

def check_s(hand):
  hand = dup_ace(hand)
  hand = elim_dups(hand)
  for i in range(len(hand) - 1, 3, -1):
    success = True
    for j in range(i - 1, i - 5, -1):
      if hand[j][0] != hand[j + 1][0] - 1:
        success = False
        break
    if success:
      return (S, [hand[i]])
  return None

def check_f(hand):
  hand = sorted(hand, key=lambda x: (x[1], x[0]))
  for i in range(len(hand) - 1, 3, -1):
    success = True
    for j in range(i - 1, i - 5, -1):
      if hand[j][1] != hand[j + 1][1]:
        success = False
        break
    if success:
      return (F, hand[i - 4:i + 1][::-1])
  return None

def check_t(hand):
  for i in range(len(hand) - 1, 1, -1):
    success = True
    for j in range(i - 1, i - 3, -1):
      if hand[j][0] != hand[j + 1][0]:
        success = False
        break
    if success:
      return (T, [hand[i]] + (hand[:i - 2] + hand[i + 1:])[-2:][::-1])
  return None

def check_tp(hand):
  first_pair = None
  high_card = None
  idx = len(hand) - 2
  while idx >= 0:
    if hand[idx][0] == hand[idx + 1][0]:
      if first_pair is None:
        first_pair = hand[idx]
      else:
        return (TP, [first_pair, hand[idx], high_card if high_card is not None else hand[idx - 1]])
      idx -= 2
    else:
      if high_card is None:
        high_card = hand[idx + 1]
      idx -= 1
  return None

def check_p(hand):
  for i in range(len(hand) - 1, 0, -1):
    if hand[i - 1][0] == hand[i][0]:
      return (P, [hand[i]] + (hand[:i - 1] + hand[i + 1:])[-3:][::-1])
  return None

def check_h(hand):
  return (H, hand[len(hand) - 5:][::-1])

def get_hand(hand):
  hand = map(lambda x: (x % 13, x / 13), hand)
  hand = sorted(hand)
  fns = [check_sf, check_q, check_fh, check_f, check_s, check_t, check_tp, check_p]
  for fn in fns:
    result = fn(hand)
    if result is not None:
      return result
  return check_h(hand)

# --------------------

players = int(sys.argv[1])

face = ['J', 'Q', 'K', 'A']
suit = ['c', 's', 'h', 'd']

def tuple_to_card(t):
  return (str(t[0] + 2) if t[0] < 9 else face[t[0] - 9]) + suit[t[1]]

def idx_to_card(i):
  return tuple_to_card((i % 13, i / 13))

deck = [i for i in range(52)]

seed = int(time.time())
print "Seed: %d" % seed
print
random.seed(seed)

random.shuffle(deck)

for i in range(players):
  print "Player %d: %s, %s" % (i, idx_to_card(deck[2 * i]), idx_to_card(deck[2 * i + 1]))

print
print ", ".join(map(lambda x: idx_to_card(deck[2 * players + x]), range(5)))

results = []
for i in range(players):
  results.append((i, get_hand(deck[2 * i:2 * i + 2] + deck[2 * players:2 * players + 5])))
results.sort(key=lambda x: x[1][0])
top_hand = results[0][1][0]
winner = results[0]
chops = []
for r in results[1:]:
  if r[1][0] == top_hand:
    best = None
    for new, cur in zip(r[1][1], winner[1][1]):
      if cur[0] > new[0]:
        best = 0
        break
      elif new[0] > cur[0]:
        best = 1
        break
    if best is not None:
      if best == 1:
        winner = r
        chops = []
    else:
      chops.append(r)
  else:
    break

print
print "Player %d wins with %s (%s)" % (winner[0], names[winner[1][0]], ", ".join(map(tuple_to_card, winner[1][1])))
for c in chops:
  print "Player %d chops (%s)" % (c[0], ", ".join(map(tuple_to_card, c[1][1])))

