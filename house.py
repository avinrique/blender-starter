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
