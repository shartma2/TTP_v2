import re  ################ PARSING ###################

def main(input: str):
    sbd_textt = extract_sbd_section(input)

    parsed_sbd = parse_sbd(sbd_textt)
    #print("Parsed SBD::", parsed_sbd)

    sid_list = parse_sid(input.strip())
    process = {
        "SID": sid_list
    }

    return(parsed_sbd, sid_list)

def parse_sid(sid_text):
    pattern = re.compile(r"\d+\.\s*(.+?)\s*->\s*(.+?):\s*(.+)")
    sid = []
    for line in sid_text.splitlines():
        match = pattern.match(line.strip())
        if match:
            sender = match.group(1).strip()
            receiver = match.group(2).strip()
            message = match.group(3).strip()
            sid.append((f"{sender} -> {receiver}", message))
    return sid

def extract_sbd_section(full_text):
    lines = full_text.splitlines()
    sbd_start = None
    for i, line in enumerate(lines):
         if "SBD" in line.upper():
            sbd_start = i + 1  # start after this line
            break
    if sbd_start is None:
        #("No SBD section found!")
        return ""

    # Extract until explanation or EOF
    sbd_lines = []
    for line in lines[sbd_start:]:
        if line.strip().startswith("### Explanation"):
            break
        sbd_lines.append(line)

    return "\n".join(sbd_lines).strip()

def parse_sbd(sbd_text):
    #print("=== SBD Text to parse ===")
    #print(sbd_text)
    #print("=========================")
    lines = sbd_text.splitlines()

    sbd = {}
    current_system = None
    states = {}
    current_state = None
    current_state_num = None
    choices = []
    branches = []
    parsing_choices = False
    parsing_branches = False

   
    actor_header_re = re.compile(r"^\s*####\s*(.+?):\s*$")
    state_header_re = re.compile(r"(\d+)\.\s+\*{0,2}(\w+)\*{0,2}:\s*(.*)")
    goto_re = re.compile(r"(\d+)\.\s+\*{0,2}GotoStep\*{0,2}:\s*(\d+)")
    choice_re = re.compile(r"-\s*From:\s*(.*)")
    branch_step_re = re.compile(r"-\s*Step:\s*(\d+)")
    branch_desc_re = re.compile(r"Description:\s*(.*)")

    for idx, line in enumerate(lines):
        line = line.rstrip()
        if not line:
            continue

        # Detect actor header
        m = actor_header_re.match(line)
        if m:
             # Finalize the current state
            if current_state is not None:
                if choices:
                    current_state["Choices"] = choices
                if branches:
                    current_state["Branches"] = branches
                if current_state["num"] not in states:
                    states[current_state["num"]] = current_state
                else:
                    existing = states[current_state["num"]]
                    existing.update({k: v for k, v in current_state.items() if k not in existing or k in ("Choices", "Branches")})

            # Save states of previous actor
            if current_system is not None:
                #print(f"\nFinalized actor: {current_system}")
                #print(f"States: {list(states.values())}")
                sbd[current_system] = list(states.values())
                
            
            # Debug
            #print(f"Detected actor: {m.group(1)}")

              

            current_system = m.group(1)
            states = {}
            current_state = None
            current_state_num = None
            choices = []
            branches = []
            parsing_choices = False
            parsing_branches = False
            continue

        if current_system is None:
            # Haven't detected an actor header yet
            current_system = "Default"
            states = {}
            

        m = goto_re.match(line)
        if m:
            current_state_num = int(m.group(1))
            next_step = int(m.group(2))
            current_state = {
                "type": "GotoStep",
                "description": f"Goto step {next_step}",
                "num": current_state_num,
                "GotoStep": next_step
            }
            
            continue

        
                
        m = state_header_re.match(line)
        if m:
           
            # Finalize previous state
            if current_state is not None:
                if choices:
                    #print(f"Parsed choices for state {current_state['num']}: {choices}")
                    current_state["Choices"] = choices
                    choices = []
                if branches:
                    #print(f"Parsed branches for state {current_state['num']}: {branches}")
                    current_state["Branches"] = branches
                    branches = []
                states[current_state["num"]] = current_state

            parsing_choices = False
            parsing_branches = False


            current_state_num = int(m.group(1))
            state_type = m.group(2)
            description = m.group(3).strip()
            current_state = {
                "type": state_type,
                "description": description,
                "num": current_state_num
            }
            
            # Check next line for edge description, but only if it's StartState or DoState with no branches
            
            if state_type in ["StartState", "DoState"]:
                # Only look ahead if it's not followed by "Branches:"
                next_lines = lines[idx+1:idx+3]  # Look ahead one or two lines safely
                has_branches_soon = any(l.strip() == "Branches:" for l in next_lines)
                if not has_branches_soon:
                    for next_line in next_lines:
                        next_line = next_line.strip()
                        if next_line.startswith("Description:"):
                            current_state["OutgoingLabel"] = next_line.split(":", 1)[1].strip()
                            break

            states[current_state_num] = current_state
            parsing_choices = False
            parsing_branches = False
            continue

        if current_state is None:
            continue

        # Handle SendState To: and Msg:
        if current_state["type"] == "SendState":
            if line.strip().startswith("To:"):
                current_state["To"] = line.split(":",1)[1].strip()
                continue
            if line.strip().startswith("Msg:"):
                current_state["Msg"] = line.split(":",1)[1].strip()
                continue

        
        # Detect Choices and Branches
        if line.strip() == "Choices:":
            if current_state is not None and choices:
                #print(f"Parsed choices for state {current_state['num']}: {choices}")
                current_state["Choices"] = choices
                choices = []
            parsing_choices = True
            parsing_branches = False
            
            continue

        elif line.strip() == "Branches:":
            # Save previously parsed branches into current_state before resetting
            if current_state is not None and branches:
                #print(f"Parsed branches for state {current_state['num']}: {branches}")
                current_state["Branches"] = branches
                branches = []
            parsing_branches = True
            parsing_choices = False
            
            continue
        

        if parsing_choices:
            m = choice_re.match(line.strip())
            
            if m:
                choices.append({"From": m.group(1).strip()})
            elif line.strip().startswith("Msg:") and choices:
                choices[-1]["Msg"] = line.split(":",1)[1].strip()
            elif line.strip().startswith("Next:") and choices:
                choices[-1]["Next"] = int(line.split(":",1)[1].strip())
            continue

        if parsing_branches:
            m = branch_step_re.match(line.strip())
            if m:
                branches.append({"Step": int(m.group(1))})
            m = branch_desc_re.match(line.strip())
            if m and branches:
                branches[-1]["Description"] = m.group(1).strip()
            continue

    # Save last state's choices or branches
    if current_state is not None:
        if choices:
            current_state["Choices"] = choices
        if branches:
            current_state["Branches"] = branches
        if current_state["num"] not in states:
            states[current_state["num"]] = current_state
        else:
            # Merge new info into existing state
            existing = states[current_state["num"]]
            existing.update({k: v for k, v in current_state.items() if k not in existing or k in ("Choices", "Branches")})
        

    # Save last actor's states
    
    # Save last state's choices or branches
    if current_state is not None:
        if choices:
            current_state["Choices"] = choices
        if branches:
            current_state["Branches"] = branches
        if current_state["num"] not in states:
            states[current_state["num"]] = current_state
        else:
            existing = states[current_state["num"]]
            existing.update({k: v for k, v in current_state.items() if k not in existing or k in ("Choices", "Branches")})

    # Finalize the last actor block (very important!)
    if current_system is not None: 
        #print(f"\nFinalized actor: {current_system}")
        #print(f"States: {list(states.values())}")
        sbd[current_system] = list(states.values())

    return sbd
