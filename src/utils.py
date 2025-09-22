def get_level_from_xp(xp : int, level_caps : list[int]) -> int:
  for level, cap in enumerate(level_caps):
    if int(cap) > xp:
      return level
  return len(level_caps)