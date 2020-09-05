#!/usr/bin/env python3

from nbtschematic import SchematicFile, BlockEntity
import nbtlib as nbt
from sys import argv
from enum import Enum
from numpy import lcm
from math import ceil, gcd

class PolyphonyException(Exception):
    pass

class TorchTowerException(Exception):
    pass

class BlockID(Enum):
    air = 0
    planks = 5
    note_block = 25
    sticky_piston = 29
    gold_block = 41
    redstone_dust = 55
    lever = 69
    redstone_torch = 76
    glowstone = 89
    redstone_repeater = 93
    wooden_slab = 126
    redstone_block = 152
    packed_ice = 174

class WoodState(Enum):
    birch = 2
    dark_oak = 5
    upside_down_dark_oak = 13

class RedstoneTorchState(Enum):
    up = 0
    east = 1
    west = 2
    south = 3
    north = 4

class RedstoneRepeaterState(Enum):
    north_1 = 0
    north_2 = 4
    north_3 = 8
    north_4 = 12
    east_1 = 1
    east_2 = 5
    east_3 = 9
    east_4 = 13
    south_1 = 2
    south_2 = 6
    south_3 = 10
    south_4 = 14
    west_1 = 3
    west_2 = 7
    west_3 = 11
    west_4 = 15

class PistonState(Enum):
    down = 0
    up = 1
    north = 2
    south = 3
    west = 4
    east = 5

class Block():
    def __init__(self, block_id, data):
        self.id = block_id
        self.data = data

class Direction(Enum):
    north = 0
    east = 1
    south = 2
    west = 3
    up = 4
    down = 5

class Instrument(Enum):
    bell = 0
    chime = 1
    harp = 2
    pling = 3
    bass = 4

note_parser = {
    "F#7":  (Instrument.bell, 24),
    "F7":   (Instrument.bell, 23),
    "E7":   (Instrument.bell, 22),
    "D#7":  (Instrument.bell, 21),
    "D7":   (Instrument.bell, 20),
    "C#7":  (Instrument.bell, 19),
    "C7":   (Instrument.bell, 18),
    "B7":   (Instrument.bell, 17),
    "A#7":  (Instrument.bell, 16),
    "A7":   (Instrument.bell, 15),
    "G#6":  (Instrument.bell, 14),
    "G6":   (Instrument.bell, 13),
    "F#6":  (Instrument.bell, 12),
    "F6":   (Instrument.bell, 11),
    "E6":   (Instrument.bell, 10),
    "D#6":  (Instrument.bell, 9),
    "D6":   (Instrument.bell, 8),
    "C#6":  (Instrument.bell, 7),
    "C6":   (Instrument.bell, 6),
    "B6":   (Instrument.bell, 5),
    "A#6":  (Instrument.bell, 4),
    "A6":   (Instrument.bell, 3),
    "G#5":  (Instrument.bell, 2),
    "G5":   (Instrument.bell, 1),
    "F#5":  (Instrument.harp, 24),
    "F5":   (Instrument.harp, 23),
    "E5":   (Instrument.harp, 22),
    "D#5":  (Instrument.harp, 21),
    "D5":   (Instrument.harp, 20),
    "C#5":  (Instrument.harp, 19),
    "C5":   (Instrument.harp, 18),
    "B5":   (Instrument.harp, 17),
    "A#5":  (Instrument.harp, 16),
    "A5":   (Instrument.harp, 15),
    "G#4":  (Instrument.harp, 14),
    "G4":   (Instrument.harp, 13),
    "F#4":  (Instrument.harp, 12),
    "F4":   (Instrument.harp, 11),
    "E4":   (Instrument.harp, 10),
    "D#4":  (Instrument.harp, 9),
    "D4":   (Instrument.harp, 8),
    "C#4":  (Instrument.harp, 7),
    "C4":   (Instrument.harp, 6),
    "B4":   (Instrument.harp, 5),
    "A#4":  (Instrument.harp, 4),
    "A4":   (Instrument.harp, 3),
    "G#3":  (Instrument.harp, 2),
    "G3":   (Instrument.harp, 1),
    "F#3":  (Instrument.harp, 0),
    "F3":   (Instrument.bass, 23),
    "E3":   (Instrument.bass, 22),
    "D#3":  (Instrument.bass, 21),
    "D3":   (Instrument.bass, 20),
    "C#3":  (Instrument.bass, 19),
    "C3":   (Instrument.bass, 18),
    "B3":   (Instrument.bass, 17),
    "A#3":  (Instrument.bass, 16),
    "A3":   (Instrument.bass, 15),
    "G#2":  (Instrument.bass, 14),
    "G2":   (Instrument.bass, 13),
    "F#2":  (Instrument.bass, 12),
    "F2":   (Instrument.bass, 11),
    "E2":   (Instrument.bass, 10),
    "D#2":  (Instrument.bass, 9),
    "D2":   (Instrument.bass, 8),
    "C#2":  (Instrument.bass, 7),
    "C2":   (Instrument.bass, 6),
    "B2":   (Instrument.bass, 5),
    "A#2":  (Instrument.bass, 4),
    "A2":   (Instrument.bass, 3),
    "G#1":  (Instrument.bass, 2),
    "G1":   (Instrument.bass, 1),
    "F#1":  (Instrument.bass, 0)
}

INSTRUMENT_BLOCK = {
    Instrument.bell: Block(BlockID.gold_block, None),
    Instrument.chime: Block(BlockID.packed_ice, None),
    Instrument.harp: Block(BlockID.air, None),
    Instrument.pling: Block(BlockID.glowstone, None),
    Instrument.bass: Block(BlockID.planks, WoodState.dark_oak)
}

REDSTONE_TORCH_BLOCK = {
    Direction.north: Block(BlockID.redstone_torch, RedstoneTorchState.north),
    Direction.east: Block(BlockID.redstone_torch, RedstoneTorchState.east),
    Direction.south: Block(BlockID.redstone_torch, RedstoneTorchState.south),
    Direction.west: Block(BlockID.redstone_torch, RedstoneTorchState.west),
    Direction.up: Block(BlockID.redstone_torch, RedstoneTorchState.up)
}

REDSTONE_REPEATER_BLOCK = {
    Direction.north: {
        1: Block(BlockID.redstone_repeater, RedstoneRepeaterState.north_1),
        2: Block(BlockID.redstone_repeater, RedstoneRepeaterState.north_2),
        3: Block(BlockID.redstone_repeater, RedstoneRepeaterState.north_3),
        4: Block(BlockID.redstone_repeater, RedstoneRepeaterState.north_4)
    },
    Direction.east: {
        1: Block(BlockID.redstone_repeater, RedstoneRepeaterState.east_1),
        2: Block(BlockID.redstone_repeater, RedstoneRepeaterState.east_2),
        3: Block(BlockID.redstone_repeater, RedstoneRepeaterState.east_3),
        4: Block(BlockID.redstone_repeater, RedstoneRepeaterState.east_4)
    },
    Direction.south: {
        1: Block(BlockID.redstone_repeater, RedstoneRepeaterState.south_1),
        2: Block(BlockID.redstone_repeater, RedstoneRepeaterState.south_2),
        3: Block(BlockID.redstone_repeater, RedstoneRepeaterState.south_3),
        4: Block(BlockID.redstone_repeater, RedstoneRepeaterState.south_4)
    },
    Direction.west: {
        1: Block(BlockID.redstone_repeater, RedstoneRepeaterState.west_1),
        2: Block(BlockID.redstone_repeater, RedstoneRepeaterState.west_2),
        3: Block(BlockID.redstone_repeater, RedstoneRepeaterState.west_3),
        4: Block(BlockID.redstone_repeater, RedstoneRepeaterState.west_4)
    }
}

STICKY_PISTON_BLOCK = {
    Direction.north: Block(BlockID.sticky_piston, PistonState.north),
    Direction.east: Block(BlockID.sticky_piston, PistonState.east),
    Direction.south: Block(BlockID.sticky_piston, PistonState.south),
    Direction.west: Block(BlockID.sticky_piston, PistonState.west),
    Direction.up: Block(BlockID.sticky_piston, PistonState.up),
    Direction.down: Block(BlockID.sticky_piston, PistonState.down)
}

TPS = 20.0
REDSTONE_MAX = 15
LINE_BLOCK = Block(BlockID.planks, WoodState.birch)
WIRING_BLOCK = Block(BlockID.planks, WoodState.dark_oak)
WIRING_SLAB = Block(BlockID.wooden_slab, WoodState.upside_down_dark_oak)

def parse_duration(lcd, duration):
    if "/" in duration:
        num, denom = [int(x) for x in duration.split("/")]
        return num * int(lcd / denom)
    return int(duration) * lcd

def parse_file(filename):
    f = open(filename, "r")
    song_info = {
        "notes": [],
        "max_denom": 1,
        "lcd": 1
    }
    for line in f:
        tokens = line.split()
        notes = tokens[0:-1]
        duration = tokens[-1]
        song_info["notes"].append((notes, duration))
        if "/" in duration:
            denom = int(duration.split("/")[1])
            song_info["lcd"] = lcm(denom, song_info["lcd"])
    song_info["length"] = 0
    for notes, duration in song_info["notes"]:
        song_info["length"] += parse_duration(song_info["lcd"], duration)
    return song_info

def list_bpms(song_info, min_bpm):
    bpms = []
    interval = 1
    bpm = 60.0 / (interval * song_info["lcd"] / TPS)
    while bpm >= min_bpm:
        bpms.append((bpm, interval))
        interval += 1
        bpm = 60.0 / (interval * song_info["lcd"] / TPS)
    return bpms

def place_block(sf, x, y, z, offset_x, offset_y, offset_z, block):
    x += offset_x
    y += offset_y
    z += offset_z
    sf.blocks[y, z, x] = block.id.value
    sf.data[y, z, x] = 0
    if block.data is not None:
        sf.data[y, z, x] = block.data.value

def place_note_block(sf, x, y, z, offset_x, offset_y, offset_z, instrument,
    pitch):
    place_block(sf, x, y, z, offset_x, offset_y, offset_z,
        Block(BlockID.note_block, None))
    sf.blockentities.append(BlockEntity({
        "id": nbt.String("noteblock"),
        "note": nbt.Byte(pitch),
        "x": nbt.Int(x + offset_x),
        "y": nbt.Int(y + offset_y),
        "z": nbt.Int(z + offset_z)
    }))
    block = INSTRUMENT_BLOCK[instrument]
    place_block(sf, x, y, z, offset_x, offset_y - 1, offset_z, block)
    return block

def copy_area(sf, src_x_lo, src_y_lo, src_z_lo, src_x_hi, src_y_hi, src_z_hi,
    dest_x_lo, dest_y_lo, dest_z_lo, dest_x_hi, dest_y_hi, dest_z_hi):
    for src_x, dest_x in zip(range(src_x_lo, src_x_hi + 1),
        range(dest_x_lo, dest_x_hi + 1)):
        for src_y, dest_y in zip(range(src_y_lo, src_y_hi + 1),
            range(dest_y_lo, dest_y_hi + 1)):
            for src_z, dest_z in zip(range(src_z_lo, src_z_hi + 1),
                range(dest_z_lo, dest_z_hi + 1)):
                sf.blocks[dest_y, dest_z, dest_x] = sf.blocks[src_y, src_z,
                    src_x]
                sf.data[dest_y, dest_z, dest_x] = sf.data[src_y, src_z, src_x]

def stack_area(sf, x_lo, y_lo, z_lo, x_hi, y_hi, z_hi, up_times, east_times,
    south_times):
    height = y_hi - y_lo + 1
    for i in range(up_times):
        copy_area(sf, x_lo, y_lo, z_lo, x_hi, y_hi, z_hi, x_lo,
            y_lo + (i + 1) * height, z_lo, x_hi, y_hi + (i + 1) * height, z_hi)
    
    width = z_hi - z_lo + 1
    y_hi = y_hi + up_times * height
    for i in range(east_times):
        copy_area(sf, x_lo, y_lo, z_lo, x_hi, y_hi, z_hi, x_lo,
            y_lo, z_lo + (i + 1) * width, x_hi, y_hi, z_hi + (i + 1) * width)
    
    depth = x_hi + x_lo + 1
    z_hi = z_hi + up_times * width
    for i in range(south_times):
        copy_area(sf, x_lo, y_lo, z_lo, x_hi, y_hi, z_hi, x_lo + (i + 1) *
            depth, y_lo, z_lo, x_hi + (i + 1) * depth, y_hi, z_hi)


def cycle_area_down(sf, x_lo, y_lo, z_lo, x_hi, y_hi, z_hi, times):
    # https://www.geeksforgeeks.org/array-rotation/
    height = y_hi - y_lo + 1
    for x in range(x_lo, x_hi + 1):
        for z in range(z_lo, z_hi + 1):
            for i in range(gcd(times, height)):
                temp_block = sf.blocks[y_lo + i, z, x]
                temp_data = sf.data[y_lo + i, z, x]
                j = i
                while True:
                    k = j + times
                    if k >= height:
                        k = k - height
                    if k == i:
                        break
                    sf.blocks[y_lo + j, z, x] = sf.blocks[y_lo + k, z, x]
                    sf.data[y_lo + j, z, x] = sf.data[y_lo + k, z, x]
                    j = k
                sf.blocks[y_lo + j, z, x] = temp_block
                sf.data[y_lo + j, z, x] = temp_data

def gen_lines(sf, x, y, z, rows, cols, length, block):
    for col in range(cols):
        for row in range(rows):
            for depth in range(length):
                place_block(sf, x, y, z, depth, row * 2, col * 2, block)
                place_block(sf, x, y, z, depth, row * 2 + 1, col * 2,
                    Block(BlockID.redstone_dust, None))

def gen_notes(sf, x, y, z, rows, cols, depth_max, song_info):
    prev_allocs = []
    depth_reached = 0
    i = 0
    for chord, duration in song_info["notes"]:
        col = int(i / rows)
        row = i % rows
        y_base = 2 * (rows - row) - 1
        z_base = col * 2 + 1
        if row == 0:
            prev_allocs = []
        allocs = []
        attempt = 0
        for note in chord:
            while attempt in prev_allocs:
                attempt += 1
                if attempt >= depth_max:
                    raise PolyphonyException
            instrument, pitch = note_parser[note]
            block = place_note_block(sf, x, y, z, attempt, y_base, z_base,
                instrument, pitch)
            if block.id != BlockID.air:
                allocs.append(attempt)
            depth_reached = max(depth_reached, attempt + 1)
            attempt += 1
        prev_allocs = allocs
        i += parse_duration(song_info["lcd"], duration)
    return depth_reached

def gen_delay_staircase(sf, x, y, z, delay, block, slab):
    depth_max = int(delay / 8) + 2
    
    place_block(sf, x, y, z, 0, 0, 0, Block(BlockID.redstone_dust, None))
    place_block(sf, x, y, z, 0, 1, 0, block)
    place_block(sf, x, y, z, 0, 3, 0, block)

    for depth in range(depth_max - 2):
        place_block(sf, x, y, z, 1 + depth, 0, 0, block)
        place_block(sf, x, y, z, 1 + depth, 1, 0,
            REDSTONE_REPEATER_BLOCK[Direction.west][4])
        place_block(sf, x, y, z, 1 + depth, 2, 0, block)
        place_block(sf, x, y, z, 1 + depth, 3, 0,
            REDSTONE_REPEATER_BLOCK[Direction.east][4])
    
    place_block(sf, x, y, z, depth_max - 1, 0, 0,
        Block(BlockID.planks, WoodState.dark_oak))
    if delay <= 4:
        place_block(sf, x, y, z, depth_max - 1, 0, 0,
            Block(BlockID.wooden_slab, WoodState.upside_down_dark_oak))
    
    delay = delay % 8 if delay % 8 > 0 else 8
    place_block(sf, x, y, z, depth_max - 1, 1, 0,
        REDSTONE_REPEATER_BLOCK[Direction.west][min(4, delay)])
    place_block(sf, x, y, z, depth_max - 1, 2, 0, block)
    if delay > 4:
        place_block(sf, x, y, z, depth_max - 1, 3, 0,
            REDSTONE_REPEATER_BLOCK[Direction.east][delay - 4])
        place_block(sf, x, y, z, depth_max, 3, 0, block)
    else:
        place_block(sf, x, y, z, depth_max - 1, 3, 0,
            Block(BlockID.redstone_dust, None))
    place_block(sf, x, y, z, depth_max, 1, 0, block)
    place_block(sf, x, y, z, depth_max, 2, 0,
        Block(BlockID.redstone_dust, None))

    return depth_max + 1

def gen_torch_tower(sf, x, y, z, height, block):
    for i in range(height):
        if i % 2 == 0:
            place_block(sf, x, y, z, 0, i, 0, block)
        else:
            place_block(sf, x, y, z, 0, i, 0,
                REDSTONE_TORCH_BLOCK[Direction.up])

def gen_engine(sf, x, y, z, rows, cols, tick_interval, block, slab):
    place_block(sf, x, y, z, 0, 0, 0, REDSTONE_TORCH_BLOCK[Direction.north])
    place_block(sf, x, y, z, 0, 1, 0, slab)
    place_block(sf, x, y, z, 0, 2, 0,
        REDSTONE_REPEATER_BLOCK[Direction.west][1])
    
    stair_depth = gen_delay_staircase(sf, x + 1, y, z, tick_interval,
        block, slab)
    cycle_area_down(sf, x + 1, y, z, x + 1 + stair_depth, y + 3, z, 2)
    gen_delay_staircase(sf, x, y, z + 1, tick_interval, block, slab)
    cycle_area_down(sf, x, y, z + 1, x + stair_depth, y + 3, z + 1, 3)
    stack_area(sf, x, y, z, x + 1 + stair_depth, y + 3, z + 1,
        int(rows / 2) - 1, 0, 0)
    
    # Clean up top and bottom of staircase
    for x_i in range(stair_depth - 1):
        place_block(sf, x, y, z, 1 + x_i, rows * 2 - 1, 1,
            Block(BlockID.air, None))
        place_block(sf, x, y, z, 2 + x_i, 0, 0, Block(BlockID.air, None))
        place_block(sf, x, y, z, 2 + x_i, 1, 0, Block(BlockID.air, None))
        place_block(sf, x, y, z, 1 + x_i, 0, 1, Block(BlockID.air, None))

    # Generate torch towers
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 3, 0,
        REDSTONE_TORCH_BLOCK[Direction.south])
    place_block(sf, x, y, z, 2 + stair_depth, 2 * rows - 3, 0, block)
    place_block(sf, x, y, z, stair_depth, 2 * rows - 3, 1, block)
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 3, 1, block)
    place_block(sf, x, y, z, 2 + stair_depth, 2 * rows - 3, 1,
        REDSTONE_TORCH_BLOCK[Direction.south])
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 2, 0, block)
    place_block(sf, x, y, z, 2 + stair_depth, 2 * rows - 2, 0,
        REDSTONE_TORCH_BLOCK[Direction.south])
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 2, 1,
        REDSTONE_TORCH_BLOCK[Direction.south])
    place_block(sf, x, y, z, 2 + stair_depth, 2 * rows - 2, 1, block)
    place_block(sf, x, y, z, 2 + stair_depth, 2 * rows - 1, 0, block)
    delay_remaining = tick_interval * (int(rows / 2) - 1) - 5
    row_select = -1
    for row in range(1, rows):
        delay_lo = (tick_interval + 2) * row
        if delay_remaining < delay_lo:
            raise TorchTowerException
        delay_hi = (tick_interval + 2) * row + 7
        if delay_remaining <= delay_hi:
            row_select = row
            break
    if row_select == -1:
        raise TorchTowerException
    place_block(sf, x, y, z, stair_depth, 2 * rows - 4 * row - 6, 1, block)
    place_block(sf, x, y, z, stair_depth, 2 * rows - 4 * row - 5, 1,
        Block(BlockID.redstone_dust, None))
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 4 * row - 5, 1, block)
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 4 * row - 4, 0, block)
    place_block(sf, x, y, z, stair_depth, 2 * rows - 4 * row - 4, 1, block)
    place_block(sf, x, y, z, 2 + stair_depth, 2 * rows - 4 * row - 4, 0,
        REDSTONE_TORCH_BLOCK[Direction.east])
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 4 * row - 4, 1,
        REDSTONE_TORCH_BLOCK[Direction.up])
    delay_remaining -= row * tick_interval
    gen_torch_tower(sf, x + 2 + stair_depth, y + 2 * rows - 4 * row - 3, z,
        4 * row, block)
    gen_torch_tower(sf, x + 1 + stair_depth, y + 2 * rows - 4 * row - 3, z + 1,
        4 * row, block)
    delay_remaining -= 2 * row
    if delay_remaining >= 4:
        place_block(sf, x, y, z, stair_depth - 1, 2 * rows - 3, 1, block)
        place_block(sf, x, y, z, stair_depth, 2 * rows - 2, 0, block)
        place_block(sf, x, y, z, stair_depth - 1, 2 * rows - 2, 1,
            REDSTONE_REPEATER_BLOCK[Direction.west][4])
        place_block(sf, x, y, z, stair_depth, 2 * rows - 1, 0,
            REDSTONE_REPEATER_BLOCK[Direction.west][4])
        delay_remaining -= 4
    place_block(sf, x, y, z, stair_depth, 2 * rows - 2, 1,
        REDSTONE_REPEATER_BLOCK[Direction.west][1 + delay_remaining])
    place_block(sf, x, y, z, 1 + stair_depth, 2 * rows - 1, 0,
        REDSTONE_REPEATER_BLOCK[Direction.west][1 + delay_remaining])
    place_block(sf, x, y, z, stair_depth + 1, 2 * rows - 7, 0,
        REDSTONE_TORCH_BLOCK[Direction.west])
    place_block(sf, x, y, z, stair_depth, 2 * rows - 7, 1,
        REDSTONE_TORCH_BLOCK[Direction.west])
    place_block(sf, x, y, z, stair_depth + 1, 2 * rows - 6, 0, block)
    place_block(sf, x, y, z, stair_depth + 2, 2 * rows - 6, 0,
        REDSTONE_TORCH_BLOCK[Direction.east])
    place_block(sf, x, y, z, stair_depth, 2 * rows - 6, 1, block)
    place_block(sf, x, y, z, stair_depth + 1, 2 * rows - 6, 1,
        REDSTONE_TORCH_BLOCK[Direction.east])

    stack_area(sf, x, y, z, x + 2 + stair_depth,
        y + int(rows / 2) * 4 - 1, z + 1, 0, cols - 1, 0)

    # Final cleanup
    for x_i in range(stair_depth):
        place_block(sf, x, y, z, 1 + x_i, 2 * rows - 3, 1,
            Block(BlockID.air, None))
        place_block(sf, x, y, z, 2 + x_i, 2 * rows - 2, 0,
            Block(BlockID.air, None))
        place_block(sf, x, y, z, 1 + x_i, 2 * rows - 2, 1,
            Block(BlockID.air, None))
        place_block(sf, x, y, z, 2 + x_i, 2 * rows - 1, 0,
            Block(BlockID.air, None))
    place_block(sf, x, y, z, stair_depth + 1, 2 * rows - 3, 0,
        Block(BlockID.air, None))
    place_block(sf, x, y, z, stair_depth + 2, 2 * rows - 2, 0,
        Block(BlockID.air, None))
    place_block(sf, x, y, z, stair_depth + 1, 2 * rows - 2, 1,
        Block(BlockID.air, None))
    place_block(sf, x, y, z, 0, 2 * rows - 2, 1, Block(BlockID.air, None))
    place_block(sf, x, y, z, 1, 2 * rows - 1, 0, Block(BlockID.air, None))
    place_block(sf, x, y, z, stair_depth, 2 * rows - 1, 0,
        Block(BlockID.air, None))
    place_block(sf, x, y, z, stair_depth + 2, 2 * rows - 1, 0,
        Block(BlockID.air, None))

def export_schematic(filename, song_info, rows):
    cols = ceil(song_info["length"] / rows)
    width_max = cols * 2
    height_max = rows * 2 + 2
    depth_max = REDSTONE_MAX + 6 + \
        int(abs((song_info["tick_interval"] - 1) / 8))
    sf = SchematicFile(shape=(height_max, width_max, depth_max))
    assert sf.shape == (height_max, width_max, depth_max)
    depth_reached = gen_notes(sf, 0, 0, 0, rows, cols, depth_max, song_info)
    gen_lines(sf, 0, 1, 0, rows, cols, depth_reached, LINE_BLOCK)
    gen_engine(sf, depth_reached, 2, 0, rows, cols, song_info["tick_interval"],
        WIRING_BLOCK, WIRING_SLAB)
    sf.save(f"{filename}.schematic")

def main():
    filename = argv[1]
    min_bpm = float(argv[2])
    rows = int(argv[3])
    song_info = parse_file(filename)

    song_info["compat_bpms"] = list_bpms(song_info, min_bpm)
    print("Please type the ID of one of the following BPM options:")
    for i, bpm_option in enumerate(song_info["compat_bpms"]):
        print(f"  {i}. {bpm_option[0]}")
    option = int(input())
    song_info["bpm"] = song_info["compat_bpms"][option][0]
    song_info["tick_interval"] = song_info["compat_bpms"][option][1]

    export_schematic(filename, song_info, rows)

if __name__ == "__main__":
    main()
