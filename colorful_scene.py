import bpy, math, random, os
HERE = "/Users/avin/projects/blender-starter"
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, rgba, metallic=0.0, roughness=0.6, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    if emission is not None:
        b.inputs["Emission Color"].default_value = emission
        b.inputs["Emission Strength"].default_value = emission_strength
    return m

# grassy ground
bpy.ops.mesh.primitive_plane_add(size=30, location=(0,0,0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(mat("ground_grass", (0.30, 0.62, 0.24, 1.0), roughness=0.95))

# ===== house =====
def add_house():
    # ---- Materials (all unique, prefixed 'house_') ----
    wall_mat   = mat("house_wall",      (0.95, 0.82, 0.18, 1.0), roughness=0.55)   # sunny yellow
    wall_mat2  = mat("house_wall_band", (0.20, 0.78, 0.92, 1.0), roughness=0.5)    # cyan accent band
    roof_mat   = mat("house_roof",      (0.92, 0.16, 0.36, 1.0), roughness=0.45)   # cherry red
    door_mat   = mat("house_door",      (0.30, 0.55, 0.95, 1.0), roughness=0.4)    # bright blue
    knob_mat   = mat("house_knob",      (1.0, 0.85, 0.10, 1.0), metallic=0.9, roughness=0.25,
                     emission=(1.0, 0.85, 0.2, 1.0), emission_strength=0.6)
    frame_mat  = mat("house_frame",     (0.95, 0.45, 0.10, 1.0), roughness=0.4)    # orange frames
    glass_mat  = mat("house_glass",     (0.55, 0.85, 0.95, 1.0), metallic=0.2, roughness=0.08,
                     emission=(0.6, 0.9, 1.0, 1.0), emission_strength=0.4)         # glassy panes
    box_mat    = mat("house_flowerbox", (0.45, 0.30, 0.18, 1.0), roughness=0.7)    # wood box
    leaf_mat   = mat("house_boxleaf",   (0.20, 0.70, 0.25, 1.0), roughness=0.6)    # greenery
    chim_mat   = mat("house_chimney",   (0.78, 0.32, 0.22, 1.0), roughness=0.85)   # brick
    chimcap_mat= mat("house_chimcap",   (0.35, 0.35, 0.40, 1.0), roughness=0.6)    # cap

    bloom_cols = [
        mat("house_bloom_0", (1.0, 0.25, 0.45, 1.0), emission=(1.0,0.3,0.5,1.0), emission_strength=0.5),
        mat("house_bloom_1", (1.0, 0.55, 0.10, 1.0), emission=(1.0,0.6,0.15,1.0), emission_strength=0.5),
        mat("house_bloom_2", (0.95, 0.85, 0.15, 1.0), emission=(1.0,0.9,0.2,1.0), emission_strength=0.5),
        mat("house_bloom_3", (0.65, 0.30, 0.95, 1.0), emission=(0.7,0.35,1.0,1.0), emission_strength=0.5),
        mat("house_bloom_4", (1.0, 0.40, 0.80, 1.0), emission=(1.0,0.45,0.85,1.0), emission_strength=0.5),
    ]

    # ---- Main wall body ----
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.4))
    body = bpy.context.active_object
    body.name = "house_body"
    body.scale = (4.4, 3.4, 2.8)  # x[-2.2,2.2] y[-1.7,1.7] z[0,2.8]
    body.data.materials.append(wall_mat)

    # ---- Color-block accent band around the walls ----
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    band = bpy.context.active_object
    band.name = "house_band"
    band.scale = (4.46, 3.46, 0.5)
    band.data.materials.append(wall_mat2)

    # ---- Roof: 4-sided pyramid cone ----
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=3.3, radius2=0.0,
                                    depth=1.6, location=(0, 0, 3.6))
    roof = bpy.context.active_object
    roof.name = "house_roof"
    roof.rotation_euler = (0, 0, math.radians(45))
    roof.scale = (1.0, 0.78, 1.0)  # match rectangular footprint
    roof.data.materials.append(roof_mat)

    # ---- Front door (faces -Y) ----
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.72, 0.75))
    door = bpy.context.active_object
    door.name = "house_door"
    door.scale = (0.9, 0.12, 1.5)
    door.data.materials.append(door_mat)

    # door frame trim
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.71, 0.78))
    dframe = bpy.context.active_object
    dframe.name = "house_doorframe"
    dframe.scale = (1.06, 0.1, 1.62)
    dframe.data.materials.append(frame_mat)

    # door knob
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0.32, -1.8, 0.75))
    knob = bpy.context.active_object
    knob.name = "house_knob"
    for p in knob.data.polygons:
        p.use_smooth = True
    knob.data.materials.append(knob_mat)

    # ---- Windows + flower boxes ----
    # (x, y, facing) ; front windows on -Y, one on +X side
    window_specs = [
        (-1.4, -1.71, "front"),
        ( 1.4, -1.71, "front"),
        ( 2.21, 0.0,  "side"),
    ]
    for i, (wx, wy, facing) in enumerate(window_specs):
        if facing == "front":
            fscale = (0.78, 0.08, 0.78)
            gscale = (0.6, 0.05, 0.6)
            fz = 1.55
            box_loc = (wx, wy - 0.12, 1.1)
            box_scale = (0.85, 0.28, 0.18)
        else:
            fscale = (0.08, 0.78, 0.78)
            gscale = (0.05, 0.6, 0.6)
            fz = 1.55
            box_loc = (wx + 0.12, wy, 1.1)
            box_scale = (0.28, 0.85, 0.18)

        # frame
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, wy, fz))
        wf = bpy.context.active_object
        wf.name = "house_winframe_%d" % i
        wf.scale = fscale
        wf.data.materials.append(frame_mat)

        # glass pane (nudged slightly outward from the wall so it shows)
        if facing == "front":
            gloc = (wx, wy - 0.02, fz)
        else:
            gloc = (wx + 0.02, wy, fz)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=gloc)
        gp = bpy.context.active_object
        gp.name = "house_glass_%d" % i
        gp.scale = gscale
        gp.data.materials.append(glass_mat)

        # flower box
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=box_loc)
        fb = bpy.context.active_object
        fb.name = "house_flowerbox_%d" % i
        fb.scale = box_scale
        fb.data.materials.append(box_mat)

        # tiny blooms in the box
        for j in range(5):
            t = (j - 2) / 2.0  # -1..1
            if facing == "front":
                bx = wx + t * 0.36
                by = wy - 0.22
            else:
                bx = wx + 0.22
                by = wy + t * 0.36
            bz = 1.24 + random.uniform(0.0, 0.05)

            # green stem stub
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.05, radius2=0.0,
                                            depth=0.12, location=(bx, by, bz - 0.04))
            st = bpy.context.active_object
            st.name = "house_boxstem_%d_%d" % (i, j)
            st.data.materials.append(leaf_mat)

            # bloom
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.07,
                                                  location=(bx, by, bz + 0.04))
            bl = bpy.context.active_object
            bl.name = "house_boxbloom_%d_%d" % (i, j)
            for p in bl.data.polygons:
                p.use_smooth = True
            bl.data.materials.append(bloom_cols[(i + j) % len(bloom_cols)])

    # ---- Brick chimney (offset on roof, +X/+Y back side) ----
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.2, 0.9, 3.6))
    chim = bpy.context.active_object
    chim.name = "house_chimney"
    chim.scale = (0.5, 0.5, 1.6)
    chim.data.materials.append(chim_mat)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.2, 0.9, 4.42))
    cap = bpy.context.active_object
    cap.name = "house_chimcap"
    cap.scale = (0.62, 0.62, 0.18)
    cap.data.materials.append(chimcap_mat)

    return body

# ===== garden =====
def add_garden():
    import colorsys

    def in_house_zone(x, y):
        return abs(x) < 2.6 and abs(y) < 2.6

    def vivid_rgba(s_min=0.75, v_min=0.85):
        h = random.random()
        s = random.uniform(s_min, 1.0)
        v = random.uniform(v_min, 1.0)
        r, gg, b = colorsys.hsv_to_rgb(h, s, v)
        return (r, gg, b, 1.0)

    stem_mat = mat("garden_stem_green", (0.20, 0.55, 0.18, 1.0), roughness=0.7)

    # ---- Flowers ----
    n_flowers = random.randint(50, 70)
    placed = 0
    attempts = 0
    while placed < n_flowers and attempts < n_flowers * 6:
        attempts += 1
        x = random.uniform(-9, 9)
        y = random.uniform(-7, 7)
        if in_house_zone(x, y):
            continue

        stem_h = random.uniform(0.4, 0.9)
        # stem
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035,
                                             depth=stem_h, location=(x, y, stem_h / 2))
        stem = bpy.context.active_object
        stem.name = "garden_stem_%d" % placed
        stem.data.materials.append(stem_mat)

        # bloom color
        bloom_rgba = vivid_rgba()
        emit = random.random() < 0.3
        bcol = mat("garden_bloom_%d" % placed, bloom_rgba, roughness=0.45,
                   emission=bloom_rgba if emit else None,
                   emission_strength=random.uniform(0.6, 1.4) if emit else 0.0)

        bloom_z = stem_h + 0.08
        if random.random() < 0.5:
            # uv sphere bloom
            r = random.uniform(0.12, 0.2)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6,
                                                 radius=r, location=(x, y, bloom_z))
            bloom = bpy.context.active_object
            bloom.scale = (1.0, 1.0, random.uniform(0.6, 0.9))
        else:
            # cone bloom (5 vertices)
            r = random.uniform(0.14, 0.24)
            bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=r, radius2=0.0,
                                            depth=random.uniform(0.18, 0.3),
                                            location=(x, y, bloom_z))
            bloom = bpy.context.active_object
            bloom.rotation_euler = (math.pi, 0, random.uniform(0, math.pi))
        bloom.name = "garden_bloom_obj_%d" % placed
        for p in bloom.data.polygons:
            p.use_smooth = True
        bloom.data.materials.append(bcol)

        # tiny bright center on some flowers
        if random.random() < 0.5:
            ccol_rgba = vivid_rgba(s_min=0.6, v_min=0.9)
            ccol = mat("garden_center_%d" % placed, ccol_rgba, roughness=0.4,
                       emission=ccol_rgba, emission_strength=random.uniform(0.5, 1.2))
            bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=5,
                                                 radius=r * 0.45,
                                                 location=(x, y, bloom_z + 0.02))
            ctr = bpy.context.active_object
            ctr.name = "garden_center_obj_%d" % placed
            for p in ctr.data.polygons:
                p.use_smooth = True
            ctr.data.materials.append(ccol)

        placed += 1

    # ---- Bushes (rounded icospheres, green variations) ----
    n_bushes = random.randint(6, 9)
    bplaced = 0
    battempts = 0
    while bplaced < n_bushes and battempts < n_bushes * 8:
        battempts += 1
        x = random.uniform(-8.5, 8.5)
        y = random.uniform(-6.5, 6.5)
        if in_house_zone(x, y):
            continue
        sz = random.uniform(0.5, 0.95)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=sz,
                                              location=(x, y, sz * 0.55))
        bush = bpy.context.active_object
        bush.name = "garden_bush_%d" % bplaced
        bush.scale = (1.0, 1.0, random.uniform(0.7, 0.95))
        # green variation
        gh = random.uniform(0.25, 0.38)
        gs = random.uniform(0.55, 0.85)
        gv = random.uniform(0.45, 0.75)
        gr, gg2, gb = colorsys.hsv_to_rgb(gh, gs, gv)
        bmat = mat("garden_bushmat_%d" % bplaced, (gr, gg2, gb, 1.0), roughness=0.8)
        for p in bush.data.polygons:
            p.use_smooth = True
        bush.data.materials.append(bmat)
        bplaced += 1

    # ---- Grass tufts (small cones clustered) ----
    n_tufts = random.randint(18, 28)
    tplaced = 0
    tattempts = 0
    while tplaced < n_tufts and tattempts < n_tufts * 6:
        tattempts += 1
        cx = random.uniform(-9, 9)
        cy = random.uniform(-7, 7)
        if in_house_zone(cx, cy):
            continue
        gh = random.uniform(0.22, 0.36)
        gs = random.uniform(0.6, 0.9)
        gv = random.uniform(0.4, 0.7)
        gr, gg2, gb = colorsys.hsv_to_rgb(gh, gs, gv)
        tmat = mat("garden_tuftmat_%d" % tplaced, (gr, gg2, gb, 1.0), roughness=0.85)
        blades = random.randint(3, 5)
        for bi in range(blades):
            ox = cx + random.uniform(-0.18, 0.18)
            oy = cy + random.uniform(-0.18, 0.18)
            bh = random.uniform(0.25, 0.5)
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.05, radius2=0.0,
                                            depth=bh, location=(ox, oy, bh / 2))
            blade = bpy.context.active_object
            blade.name = "garden_tuft_%d_%d" % (tplaced, bi)
            blade.rotation_euler = (random.uniform(-0.2, 0.2),
                                    random.uniform(-0.2, 0.2),
                                    random.uniform(0, math.pi))
            blade.data.materials.append(tmat)
        tplaced += 1

# ===== trees =====
def add_trees():
    # corner positions for the trees
    spots = [(-6, 3), (6, -4), (-7, -5), (7, 4), (-3.5, 6.5), (4.5, 5.5)]

    # foliage palettes: name, base rgba, optional emission for a little pop, strength
    palettes = [
        ("green",   (0.16, 0.52, 0.18, 1.0), None,                 0.0),
        ("green2",  (0.22, 0.60, 0.24, 1.0), None,                 0.0),
        ("pink",    (0.95, 0.55, 0.78, 1.0), (1.0, 0.6, 0.85, 1.0), 0.4),
        ("autumn",  (0.92, 0.46, 0.10, 1.0), (1.0, 0.45, 0.1, 1.0), 0.3),
        ("teal",    (0.10, 0.70, 0.66, 1.0), (0.1, 0.8, 0.75, 1.0), 0.4),
    ]
    # assign a palette per tree for a colorful storybook mix (green + pink + autumn + teal)
    assign = [0, 2, 3, 4, 1, 2]

    trunk_col = mat("trees_trunk", (0.42, 0.27, 0.13, 1.0), roughness=0.85)

    for i, (x, y) in enumerate(spots):
        pname, prgba, pemit, pstr = palettes[assign[i % len(assign)]]
        scale = random.uniform(0.9, 1.25)
        # shrink the near-camera foreground tree so it doesn't crowd the frame
        if y < 0 and x > 3:
            scale = 0.6
        rot = random.uniform(0, math.pi * 2)

        # trunk = low-poly cylinder
        th = 1.4 * scale
        tr = 0.16 * scale
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=tr, depth=th,
                                             location=(x, y, th / 2.0))
        trunk = bpy.context.active_object
        trunk.name = f"trees_trunk_{i}"
        trunk.rotation_euler = (0, 0, rot)
        trunk.data.materials.append(trunk_col)
        for p in trunk.data.polygons:
            p.use_smooth = True

        # foliage material (unique per tree)
        fmat = mat(f"trees_foliage_{i}_{pname}", prgba, roughness=0.55,
                   emission=pemit, emission_strength=pstr)

        # foliage = stacked cones for a classic storybook tree
        base_z = th
        n_cones = random.randint(3, 4)
        cone_r = 1.05 * scale
        cone_h = 1.0 * scale
        step = 0.55 * scale
        for c in range(n_cones):
            r = cone_r * (1.0 - 0.22 * c)
            z = base_z + step * c + cone_h / 2.0
            bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=r, radius2=0.0,
                                            depth=cone_h, location=(x, y, z))
            cone = bpy.context.active_object
            cone.name = f"trees_foliage_{i}_{c}"
            cone.rotation_euler = (0, 0, rot + c * 0.3)
            cone.data.materials.append(fmat)
            for p in cone.data.polygons:
                p.use_smooth = True

# ===== sky =====
def add_sky():
    # ---- RAINBOW: 7 concentric half-torus arcs in ROYGBIV ----
    roygbiv = [
        ("red",    (1.00, 0.05, 0.05, 1.0)),
        ("orange", (1.00, 0.45, 0.00, 1.0)),
        ("yellow", (1.00, 0.95, 0.05, 1.0)),
        ("green",  (0.10, 0.90, 0.15, 1.0)),
        ("blue",   (0.05, 0.35, 1.00, 1.0)),
        ("indigo", (0.30, 0.10, 0.85, 1.0)),
        ("violet", (0.70, 0.10, 0.95, 1.0)),
    ]

    base_radius = 10.0      # outer ring radius
    band = 0.55             # spacing between bands
    tube = 0.42             # thickness of each band (minor radius)
    # place the rainbow high and toward +Y, behind the house. The center sits
    # near ground level so the lower half of the big ring is below z=0 and only
    # the arc shows above the horizon.
    rainbow_origin = (0.0, 6.0, -0.5)

    for i, (cname, rgba) in enumerate(roygbiv):
        major = base_radius - i * band
        m = mat("sky_rainbow_%s_%d" % (cname, i), rgba,
                metallic=0.0, roughness=0.5,
                emission=rgba, emission_strength=2.2)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=major,
            minor_radius=tube,
            major_segments=64,
            minor_segments=10,
            location=rainbow_origin,
        )
        obj = bpy.context.active_object
        obj.name = "sky_rainbow_arc_%d" % i
        # The torus lies flat in the XY plane by default. Rotate 90deg about X so
        # the ring stands up in the XZ plane: it then arches left->up->right and
        # faces the -Y camera as a wide rainbow across the sky.
        obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        obj.data.materials.append(m)
        for p in obj.data.polygons:
            p.use_smooth = True

    # ---- GLOWING SUN DISK (high, toward +Y, off to one side) ----
    sun_mat = mat("sky_sun_disk_mat", (1.0, 0.92, 0.35, 1.0),
                  metallic=0.0, roughness=0.4,
                  emission=(1.0, 0.85, 0.25, 1.0), emission_strength=6.0)
    bpy.ops.mesh.primitive_circle_add(
        vertices=32, radius=2.4, fill_type='NGON',
        location=(-7.0, 11.0, 8.5),
    )
    sun = bpy.context.active_object
    sun.name = "sky_sun_disk"
    # face the -Y camera (disk normal points toward -Y)
    sun.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    sun.data.materials.append(sun_mat)
    for p in sun.data.polygons:
        p.use_smooth = True

    # ---- FLUFFY WHITE CLOUDS ----
    # Strongly emissive white so the clouds read as bright glowing white against
    # the sky regardless of lighting / view-transform tone-mapping. At low
    # emission they render as dark silhouettes (backlit + far away), so push it.
    cloud_mat = mat("sky_cloud_mat", (1.0, 1.0, 1.0, 1.0),
                    metallic=0.0, roughness=1.0,
                    emission=(1.0, 1.0, 1.0, 1.0), emission_strength=5.0)

    # cloud cluster anchor points: high, large, toward +Y / far side
    cloud_anchors = [
        ( 6.0,  9.0,  8.5),
        (-7.0, 12.0, 10.5),
        (-1.0, 15.0, 11.5),
        (10.0, 14.0,  7.0),
        (-5.0,  8.0,  6.0),
        ( 3.0, 13.0, 12.5),
    ]

    for ci, (ax, ay, az) in enumerate(cloud_anchors):
        n_puffs = random.randint(5, 7)
        for pi in range(n_puffs):
            ox = random.uniform(-2.4, 2.4)
            oy = random.uniform(-0.8, 0.8)
            oz = random.uniform(-0.6, 0.9)
            r = random.uniform(1.2, 2.1)
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=16, ring_count=10, radius=r,
                location=(ax + ox, ay + oy, az + oz),
            )
            puff = bpy.context.active_object
            puff.name = "sky_cloud_%d_%d" % (ci, pi)
            # squash slightly for a fluffy flat-bottom look
            puff.scale = (1.0, 1.0, random.uniform(0.6, 0.8))
            puff.data.materials.append(cloud_mat)
            for p in puff.data.polygons:
                p.use_smooth = True

# ===== props =====
def add_balloons():
    # Cluster of colorful balloons floating near the house, z 4-8
    balloon_colors = [
        (0.95, 0.15, 0.20, 1.0),  # red
        (0.20, 0.55, 0.95, 1.0),  # blue
        (1.00, 0.80, 0.10, 1.0),  # yellow
        (0.25, 0.80, 0.35, 1.0),  # green
        (0.85, 0.30, 0.85, 1.0),  # magenta
        (1.00, 0.50, 0.10, 1.0),  # orange
        (0.40, 0.85, 0.90, 1.0),  # cyan
        (0.70, 0.40, 0.95, 1.0),  # purple
    ]
    # Anchor cluster slightly off to the side near the house, floating high
    anchor_x = -3.2
    anchor_y = 0.0
    n = 9
    for i in range(n):
        col = balloon_colors[i % len(balloon_colors)]
        # spread balloons in a loose cluster
        bx = anchor_x + random.uniform(-1.3, 1.3)
        by = anchor_y + random.uniform(-1.0, 1.0)
        bz = random.uniform(3.2, 5.4)
        rad = random.uniform(0.32, 0.52)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=rad)
        b = bpy.context.active_object
        b.name = "props_balloon_%d" % i
        b.location = (bx, by, bz)
        # slight vertical stretch for balloon teardrop look
        b.scale = (1.0, 1.0, 1.18)
        b.rotation_euler = (0.0, 0.0, random.uniform(0, 6.28))
        for p in b.data.polygons:
            p.use_smooth = True
        m = mat("props_balloon_mat_%d" % i, col, metallic=0.0, roughness=0.25,
                emission=col, emission_strength=0.35)
        b.data.materials.append(m)

        # little knot at the bottom of the balloon
        knot_z = bz - rad * 1.18
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=rad * 0.18, radius2=0.0, depth=rad * 0.3)
        k = bpy.context.active_object
        k.name = "props_balloon_knot_%d" % i
        k.location = (bx, by, knot_z - rad * 0.1)
        k.rotation_euler = (math.pi, 0.0, 0.0)
        k.data.materials.append(m)

        # thin string cylinder hanging down
        str_len = bz * random.uniform(0.45, 0.75)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.015, depth=str_len)
        s = bpy.context.active_object
        s.name = "props_balloon_string_%d" % i
        s.location = (bx + random.uniform(-0.05, 0.05),
                      by + random.uniform(-0.05, 0.05),
                      knot_z - str_len / 2.0)
        sm = mat("props_balloon_string_mat_%d" % i, (0.15, 0.15, 0.15, 1.0),
                 metallic=0.0, roughness=0.8)
        s.data.materials.append(sm)


def add_bunting():
    # String of triangular bunting flags strung between two small poles
    bright = [
        (0.95, 0.20, 0.25, 1.0),
        (1.00, 0.78, 0.10, 1.0),
        (0.25, 0.75, 0.95, 1.0),
        (0.30, 0.82, 0.40, 1.0),
        (0.90, 0.35, 0.85, 1.0),
        (1.00, 0.55, 0.15, 1.0),
    ]
    # Two poles to the left side of the yard, in front area
    p1 = (-2.9, -2.4, 0.0)
    p2 = (-2.9, -5.6, 0.0)
    pole_h = 2.2
    pole_mat = mat("props_bunting_pole_mat", (0.55, 0.38, 0.22, 1.0),
                   metallic=0.0, roughness=0.7)
    for idx, (px, py, pz) in enumerate([p1, p2]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=pole_h)
        pole = bpy.context.active_object
        pole.name = "props_bunting_pole_%d" % idx
        pole.location = (px, py, pole_h / 2.0)
        for p in pole.data.polygons:
            p.use_smooth = True
        pole.data.materials.append(pole_mat)

    # The string between pole tops (a sagging line approximated as straight segments)
    top_z = pole_h - 0.1
    nflags = 9
    string_mat = mat("props_bunting_string_mat", (0.1, 0.1, 0.1, 1.0),
                     metallic=0.0, roughness=0.8)
    for i in range(nflags):
        t = (i + 0.5) / nflags
        # position along the line from p1 to p2
        fx = p1[0] + (p2[0] - p1[0]) * t
        fy = p1[1] + (p2[1] - p1[1]) * t
        # sag: parabola, lowest at middle
        sag = 0.45 * math.sin(t * math.pi)
        fz = top_z - sag

        col = bright[i % len(bright)]
        # triangular flag: cone with 3 vertices = flat triangle, pointed down
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.18, radius2=0.0, depth=0.36)
        flag = bpy.context.active_object
        flag.name = "props_bunting_flag_%d" % i
        flag.location = (fx, fy, fz - 0.22)
        # flatten into a thin triangle facing the camera (-Y), point down
        flag.scale = (1.0, 0.12, 1.0)
        flag.rotation_euler = (math.pi, 0.0, 0.0)
        fm = mat("props_bunting_flag_mat_%d" % i, col, metallic=0.0, roughness=0.45,
                 emission=col, emission_strength=0.2)
        flag.data.materials.append(fm)

    # the connecting string as a thin slightly-sagging set of segments
    segs = 12
    prev = (p1[0], p1[1], top_z)
    for i in range(1, segs + 1):
        t = i / segs
        cx = p1[0] + (p2[0] - p1[0]) * t
        cy = p1[1] + (p2[1] - p1[1]) * t
        cz = top_z - 0.45 * math.sin(t * math.pi)
        midx = (prev[0] + cx) / 2.0
        midy = (prev[1] + cy) / 2.0
        midz = (prev[2] + cz) / 2.0
        dx = cx - prev[0]
        dy = cy - prev[1]
        dz = cz - prev[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.012, depth=length)
        seg = bpy.context.active_object
        seg.name = "props_bunting_seg_%d" % i
        seg.location = (midx, midy, midz)
        # orient cylinder along the segment direction
        seg.rotation_euler = (math.acos(dz / length) if length > 0 else 0.0,
                              0.0,
                              math.atan2(dy, dx) + math.pi / 2.0)
        seg.data.materials.append(string_mat)
        prev = (cx, cy, cz)


def add_path():
    # Winding stepping-stone path of flat rounded slabs from door along -Y
    slab_mat = mat("props_path_slab_mat", (0.62, 0.60, 0.58, 1.0),
                   metallic=0.0, roughness=0.85)
    slab_mat2 = mat("props_path_slab_mat2", (0.70, 0.66, 0.60, 1.0),
                    metallic=0.0, roughness=0.85)
    n = 9
    start_y = -2.0
    end_y = -6.8
    for i in range(n):
        t = i / (n - 1)
        sy = start_y + (end_y - start_y) * t
        # winding sideways sway
        sx = math.sin(t * math.pi * 2.2) * 0.55
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=0.08)
        slab = bpy.context.active_object
        slab.name = "props_path_slab_%d" % i
        slab.location = (sx, sy, 0.04)
        slab.scale = (1.0, 0.82, 1.0)
        slab.rotation_euler = (0.0, 0.0, random.uniform(-0.4, 0.4))
        for p in slab.data.polygons:
            p.use_smooth = True
        slab.data.materials.append(slab_mat if i % 2 == 0 else slab_mat2)


def add_fence():
    # Low white picket fence with colorful post caps along part of the yard edge
    white = mat("props_fence_white", (0.95, 0.95, 0.93, 1.0),
                metallic=0.0, roughness=0.6)
    cap_colors = [
        (0.95, 0.20, 0.25, 1.0),
        (0.25, 0.60, 0.95, 1.0),
        (1.00, 0.80, 0.12, 1.0),
        (0.30, 0.82, 0.40, 1.0),
        (0.88, 0.35, 0.85, 1.0),
        (1.00, 0.55, 0.15, 1.0),
    ]
    # Run fence along the right yard edge (front-right), away from path & house
    fence_y = -6.6
    x_start = 2.8
    x_end = 8.0
    n_pickets = 11
    rail_h1 = 0.30
    rail_h2 = 0.62
    picket_h = 0.85
    picket_w = 0.10

    spacing = (x_end - x_start) / (n_pickets - 1)
    for i in range(n_pickets):
        px = x_start + spacing * i
        # vertical picket (box)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        pk = bpy.context.active_object
        pk.name = "props_fence_picket_%d" % i
        pk.scale = (picket_w, 0.05, picket_h)
        pk.location = (px, fence_y, picket_h / 2.0)
        pk.data.materials.append(white)

        # pointed cap as small cone, colorful
        col = cap_colors[i % len(cap_colors)]
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=picket_w * 0.9, radius2=0.0, depth=0.18)
        cap = bpy.context.active_object
        cap.name = "props_fence_cap_%d" % i
        cap.location = (px, fence_y, picket_h + 0.09)
        cap.rotation_euler = (0.0, 0.0, math.pi / 4.0)
        cm = mat("props_fence_cap_mat_%d" % i, col, metallic=0.0, roughness=0.4,
                 emission=col, emission_strength=0.25)
        cap.data.materials.append(cm)

    # two horizontal rails
    rail_len = x_end - x_start + picket_w
    for ridx, rh in enumerate([rail_h1, rail_h2]):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        rail = bpy.context.active_object
        rail.name = "props_fence_rail_%d" % ridx
        rail.scale = (rail_len, 0.04, 0.07)
        rail.location = ((x_start + x_end) / 2.0, fence_y, rh)
        rail.data.materials.append(white)


def add_props():
    add_balloons()
    add_bunting()
    add_path()
    add_fence()

# ===== stage =====
def setup_stage():
    scene = bpy.context.scene

    # ---- World: pleasant blue sky at gentle strength ----
    # Solid saturated blue (kept gentle) so ambient doesn't wash out the props.
    world = bpy.data.worlds.new("stage_world")
    world.use_nodes = True
    scene.world = world
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    for n in list(wnodes):
        wnodes.remove(n)
    bg = wnodes.new("ShaderNodeBackground")
    out = wnodes.new("ShaderNodeOutputWorld")
    bg.inputs["Color"].default_value = (0.18, 0.42, 0.85, 1.0)  # pleasant sky blue
    bg.inputs["Strength"].default_value = 0.45                   # gentle: vivid, not flat
    wlinks.new(bg.outputs["Background"], out.inputs["Surface"])

    # ---- Sun (moderate energy) ----
    sun_data = bpy.data.lights.new("stage_sun_light", type='SUN')
    sun_data.energy = 4.0
    sun_data.color = (1.0, 0.97, 0.92)
    sun_data.angle = math.radians(2.5)
    sun = bpy.data.objects.new("stage_sun", sun_data)
    scene.collection.objects.link(sun)
    sun.location = (5, -6, 12)
    sun.rotation_euler = (math.radians(48), math.radians(18), math.radians(30))

    # ---- Soft area fill (front, toward camera / door at -Y) ----
    # Kept moderate so it lifts shadows without desaturating base colors.
    fill_data = bpy.data.lights.new("stage_fill_light", type='AREA')
    fill_data.shape = 'RECTANGLE'
    fill_data.size = 14.0
    fill_data.size_y = 8.0
    fill_data.energy = 40.0
    fill_data.color = (0.85, 0.92, 1.0)
    fill = bpy.data.objects.new("stage_fill", fill_data)
    scene.collection.objects.link(fill)
    fill.location = (4, -12, 9)
    fill.rotation_euler = (math.radians(58), 0, math.radians(20))

    # ---- Gentle back fill from +Y so the rainbow/sky side isn't black ----
    back_data = bpy.data.lights.new("stage_back_light", type='AREA')
    back_data.shape = 'RECTANGLE'
    back_data.size = 16.0
    back_data.size_y = 10.0
    back_data.energy = 20.0
    back_data.color = (0.80, 0.88, 1.0)
    back = bpy.data.objects.new("stage_back", back_data)
    scene.collection.objects.link(back)
    back.location = (-3, 11, 9)
    back.rotation_euler = (math.radians(-58), 0, math.radians(15))

    # ---- Camera (frames house + rainbow behind it) ----
    cam_data = bpy.data.cameras.new("stage_cam_data")
    cam_data.lens = 28
    cam = bpy.data.objects.new("stage_camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (5.0, -16.0, 6.5)
    # Aim with a Track-To constraint so the house AND the rainbow/clouds behind it stay framed.
    cam_target = bpy.data.objects.new("stage_cam_target", None)
    bpy.context.collection.objects.link(cam_target)
    cam_target.location = (0.0, 4.5, 4.5)
    _trk = cam.constraints.new(type='TRACK_TO')
    _trk.target = cam_target
    _trk.track_axis = 'TRACK_NEGATIVE_Z'
    _trk.up_axis = 'UP_Y'
    scene.camera = cam

    # ---- Render engine + resolution ----
    # Blender 5.x uses BLENDER_EEVEE_NEXT; fall back to BLENDER_EEVEE on older builds.
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False

    # ---- EEVEE quality knobs (best-effort across versions) ----
    eevee = scene.eevee
    for attr, val in [
        ("taa_render_samples", 64),
        ("use_gtao", True),
        ("use_bloom", True),
        ("bloom_intensity", 0.02),
    ]:
        try:
            setattr(eevee, attr, val)
        except Exception:
            pass

    # ---- Color management: punchy, saturated, NOT blown out ----
    # 'Standard' view transform keeps colors vivid (AgX is filmic/desaturated).
    # With moderate fills, exposure 0.0 gives full-saturation hues and zero blowout.
    vs = scene.view_settings
    try:
        vs.view_transform = 'Standard'
    except TypeError:
        pass
    try:
        vs.look = 'None'
    except TypeError:
        pass
    vs.exposure = 0.0
    vs.gamma = 1.0
    try:
        scene.display_settings.display_device = 'sRGB'
    except Exception:
        pass

    return cam

# --- assemble scene ---
add_house()
add_garden()
add_trees()
add_sky()
add_props()
setup_stage()

# --- output ---
scene = bpy.context.scene
scene.render.filepath = os.path.join(OUT, "colorful_preview.png")
print(">>> rendering colorful scene")
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "colorful.blend"))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "colorful.glb"), export_format="GLB", use_selection=True)
print(">>> DONE")
