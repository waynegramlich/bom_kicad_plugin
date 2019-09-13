# MIT License
# 
# Copyright (c) 2019 Wayne C. Gramlich
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from bom_manager import bom
import csv
import os
import sexpdata                 # (LISP)S-EXPression DATA package
from sexpdata import Symbol     # (LISP) S-expression Symobl

# cad_get():
def cad_get(tracing=None):
    # Verify argument types:
    assert isinstance(tracing, str) or tracing is None

    # Perform any requested *tracing*:
    next_tracing = None if tracing is None else tracing + " "
    if tracing is not None:
        print(f"{tracing}=>findchips.py:panda_get()")

    # Create the *find_chips* object:
    kicad = Kicad(tracing=next_tracing)

    # Wrap up any requested *tracing* and return *kicad*:
    if tracing is not None:
        print(f"{tracing}<=findchips.py:panda_get()=>*")
    return kicad

# Kicad:
class Kicad(bom.Cad):

    # Kicad.__init__():
    def __init__(self, tracing=None):
        # Verify argument types:
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>Kicad.__init__()")

        # Initialize the super class of the *FindChips* object (i.e. *self*):
        super().__init__("KiCAD", tracing=next_tracing)

        # Perform any requested *tracing*:
        if tracing is not None:
            print(f"{tracing}<=Kicad.__init__()")

    # Kicad.altium_csv_read():
    def altium_csv_read(self, csv_file_name, project, tracing=None):
        # Verify argument types:
        assert isinstance(csv_file_name, str) and csv_file_name.endswith(".csv")
        assert isinstance(project, bom.Project)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>altium_csv_read(*, '{csv_file_name}')")

        # ...
        success = False
        with open(csv_file_name, encoding="iso-8859-1") as csv_file:
            csv_rows = list(csv.reader(csv_file, delimiter=",", quotechar='"'))
            actual_headers = tuple(csv_rows[0])
            if True:
                desired_headers = (
                    "Line #", "Name", "Description", "Designator", "Quantity", "TargetPrice",
                    "Manufacturer 1", "Manufacturer Part Number 1", "Manufacturer Lifecycle 1",
                    "Supplier 1", "Supplier Part Number 1", "Supplier Unit Price 1",
                    "Supplier Subtotal 1")
                for index, desired_header in enumerate(desired_headers):
                    assert desired_header == actual_headers[index], f"index={index}"
                assert (actual_headers == desired_headers), (f"Got {actual_headers} "
                                                             f"instead of {desired_headers}")
                project_parts = list()
                for index, row in enumerate(csv_rows[2:]):
                    # Unpack *row* and further split and strip *refs_text* into *refs*:
                    line_number, name, description, designators_text, quantity = row[:5]
                    designators = designators_text.split(",")
                    designators = [designator.strip() for designator in designators]
                    if tracing is not None:
                        print(f"{tracing}Row[{index}]: "
                              f"{quantity}\t'{part_name}'\t{designators_text}")

                    # Lookup/create the *project_part* associated with *value*:
                    project_part = project.project_part_find(name)

                    # Create one *pose_part* for each *reference* in *references*:
                    for designator in designators:
                        pose_part = bom.PosePart(project, project_part, designator, "")
                        project.pose_part_append(pose_part)

                    # Ignore footprints for now:
                    success = True
            else:
                assert False, (f"File '{csv_file_name}' was generated using '{generator}' "
                               "which is not supported yet.  Use "
                               "'bom_csv_grouped_by_value_with_fp' generator instead.")
            
        # Wrap up any requested *tracing* and return the *success* flag:
        if tracing is not None:
            print(f"{tracing}<=Kicad.altium_csv_read(*, '{csv_file_name}', *)=>{success}")
        return success

    # Kicad.cmp_file_read():
    def cmp_file_read(self, cmp_file_name, project, tracing=None):
        # Verify argument types:
        assert isinstance(cmp_file_name, ".cmp") and cmp_file.endswith(".cmp")
        assert isinstance(project, bom.Project)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>Kicad.cmp_file_read(*, '{cmp_file_name}, *)")

        # This code is really old, so just fail for now:
        assert False, "Kicad.cmp_file_read() needs to be fixed!!!"

        # Read in {cmp_file_name}:
        with open(cmp_file_name, "r") as cmp_stream:
            cmp_lines = cmp_stream.readlines()

            # Process each {line} in {cmp_lines}:
            database = project.database
            errors = 0
            line_number = 0
            for line in cmp_lines:
                # Keep track of {line} number for error messages:
                line_number = line_number + 1

                # There are three values we care about:
                if line.startswith("BeginCmp"):
                    # Clear out the values:
                    reference = None
                    part_name = None
                    footprint = None
                elif line.startswith("Reference = "):
                    reference = line[12:-2]
                elif line.startswith("ValeurCmp = "):
                    part_name = line[12:-2]
                    # print("part_name:{0}".format(part_name))
                    double_underscore_index = part_name.find("__")
                    if double_underscore_index >= 0:
                        shortened_part_name = \
                          part_name[:double_underscore_index]
                        # print("Shorten part name '{0}' => '{1}'".
                        #  format(part_name, shortened_part_name))
                        part_name = shortened_part_name
                elif line.startswith("IdModule  "):
                    footprint = line[12:-2].split(':')[1]
                    # print("footprint='{0}'".format(footprint))
                elif line.startswith("EndCmp"):
                    part = database.part_lookup(part_name)
                    if part is None:
                        # {part_name} not in {database}; output error message:
                        print("File '{0}', line {1}: Part Name {2} ({3} {4}) not in database".
                              format(cmp_file_name, line_number, part_name, reference, footprint))
                        errors = errors + 1
                    else:
                        footprint_pattern = part.footprint_pattern
                        if fnmatch.fnmatch(footprint, footprint_pattern):
                            # The footprints match:
                            pose_part = \
                              PosePart(project, part, reference, footprint)
                            project.pose_parts_append(pose_part)
                            part.pose_parts.append(pose_part)
                        else:
                            print(("File '{0}',  line {1}: {2}:{3} Footprint" +
                                   "'{4}' does not match database '{5}'").format(
                                   cmp_file_name, line_number,
                                   reference, part_name, footprint,
                                   footprint_pattern))
                            errors = errors + 1
                elif (line == "\n" or line.startswith("TimeStamp") or
                      line.startswith("EndListe") or line.startswith("Cmp-Mod V01")):
                    # Ignore these lines:
                    line = line
                else:
                    # Unrecognized {line}:
                    print("'{0}', line {1}: Unrecognized line '{2}'".
                          format(cmp_file_name, line_number, line))
                    errors = errors + 1

        # Wrap up any requested *tracing*:
        if tracing is not None:
            print(f"{tracing}<=Kicad.cmp_file_read(*, '{cmp_file_name}, *)=>{success}")
        return success

    # Kicad.csv_file_read():
    def bom_csv_grouped_by_value_with_fp_read(self, csv_file_name, project, tracing=None):
        # Verify argument types:
        assert isinstance(csv_file_name, str) and csv_file_name.endswith(".csv")
        assert isinstance(project, bom.Project)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>bom_csv_grouped_by_value_with_fp_read(*, '{csv_file_name}')")

        # ...
        success = False
        with open(csv_file_name) as csv_file:
            csv_rows = list(csv.reader(csv_file, delimiter=",", quotechar='"'))
            assert csv_rows[0][0] == "Source:"
            source = csv_rows[0][1]
            assert csv_rows[1][0] == "Date:"
            date = csv_rows[1],[1]
            assert csv_rows[2][0] == "Tool:"
            tool = csv_rows[2][1]
            assert csv_rows[3][0] == "Generator:"
            generator = csv_rows[3][1]
            assert csv_rows[4][0] == "Component Count:"
            component_count = int(csv_rows[4][1])
            headers = tuple(csv_rows[5])
            if generator.endswith("bom_csv_grouped_by_value_with_fp.py"):
                actual_headers = headers[0:7]
                desired_headers = (
                    "Ref", "Qnty", "Value", "Cmp name", "Footprint", "Description", "Vendor")
                for index, desired_header in enumerate(desired_headers):
                    assert desired_header == actual_headers[index], f"index={index}"
                assert (actual_headers == desired_headers), (f"Got {actual_headers} "
                                                             f"instead of {desired_headers}")
                project_parts = list()
                for index, row in enumerate(csv_rows[6:6+component_count]):
                    # Unpack *row* and further split and strip *refs_text* into *refs*:
                    references_text, quantity, part_name, component_name, footprint = row[:5]
                    references = references_text.split(",")
                    references = [reference.strip() for reference in references]
                    if tracing is not None:
                        print(f"{tracing}Row[{index}]: "
                              f"{quantity}\t'{part_name}'\t{references_text}")

                    # Strip *comment* out of *part_name* if it exists:
                    comment = ""
                    colon_index = part_name.find(':')
                    if colon_index >= 0:
                        comment = part_name[colon_index + 1:]
                        part_name = part_name[0:colon_index]

                    # Lookup/create the *project_part* associated with *value*:
                    project_part = project.project_part_find(part_name)

                    # Create one *pose_part* for each *reference* in *references*:
                    for reference in references:
                        pose_part = bom.PosePart(project, project_part, reference, comment)
                        project.pose_part_append(pose_part)

                    # Ignore footprints for now:
                    success = True
            else:
                assert False, (f"File '{csv_file_name}' was generated using '{generator}' "
                               "which is not supported yet.  Use "
                               "'bom_csv_grouped_by_value_with_fp' generator instead.")
            
        # Wrap up any requested *tracing* and return the *success* flag:
        if tracing is not None:
            print(f"{tracing}<=Kicad.bom_csv_grouped_by_value_with_fp_read(*, "
                  f"'{csv_file_name}', *)=>{success}")
        return success

    # Kicad.file_read():
    def file_read(self, file_name, project, tracing=None):
        # Verify argument types:
        assert isinstance(file_name, str)
        assert isinstance(project, bom.Project)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        success = False
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>Kicad.load(*, '{file_name}')")

        # Dispatach on the *file_name* suffix:
        kicad = self
        success = False
        assert os.path.isfile(file_name), f"File '{file_name}' does not exist"
        if file_name.endswith(".cmp"):
            success = kicad.cmp_file_read(file_name, project, tracing=next_tracing)
        elif file_name.endswith(".csv"):
            try:
                success = kicad.altium_csv_read(file_name, project, tracing=next_tracing)
            except AssertionError:
                try:
                    success = kicad.bom_csv_grouped_by_value_with_fp_read(file_name, project,
                                                                          tracing=next_tracing)
                except AsssertionError:
                    success = False
        elif file_name.endswith(".net"):
            success = kicad.net_file_read(file_name, project, tracing=next_tracing)

        # Wrap up any requested *tracing* and return the *success* flag:
        if tracing is not None:
            print(f"{tracing}<=Kicad.load(*, '{file_name}', *)=>{success}")
        return success

    # Kicad.net_file_read():
    def net_file_read(self, net_file_name, project, tracing=None):
        """ Read in net file for the project object.
        """

        # Verify argument types:
        assert isinstance(self, Kicad)
        assert isinstance(net_file_name, str) and net_file_name.endswith(".net")
        assert isinstance(project, bom.Project)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>Kicad.net_file_read(*, '{net_file_name}', *)")

        # Prevent accidental double of *project* (i.e. *self*):
        kicad = self
        pose_parts = project.all_pose_parts
        assert len(pose_parts) == 0

        # Process *net_file_name* adding footprints as needed:
        success = False
        errors = 0
        with open(net_file_name, "r") as net_stream:
            # Read contents of *net_file_name* in as a string *net_text*:
            net_text = net_stream.read()
            if tracing is not None:
                print(f"{tracing}Read in file '{net_file_name}'")

            # Parse *net_text* into *net_se* (i.e. net S-expression):
            net_se = sexpdata.loads(net_text)
            # print("\nsexpedata.dumps=", sexpdata.dumps(net_se))
            # print("")
            # print("net_se=", net_se)
            # print("")

            # Visit each *component_se* in *net_se*:
            net_file_changed = False
            #database = project.order.database
            components_se = Kicad.se_find(net_se, "export", "components")

            # Each component has the following form:
            #
            #        (comp
            #          (ref SW123)
            #          (footprint nickname:NAME)              # May not be present
            #          (libsource ....)
            #          (sheetpath ....)
            #          (tstamp xxxxxxxx))
            # print("components=", components_se)
            for component_index, component_se in enumerate(components_se[1:]):
                # print("component_se=", component_se)
                # print("")

                # Grab the *reference* from *component_se*:
                reference_se = Kicad.se_find(component_se, "comp", "ref")
                reference = reference_se[1].value()
                # print("reference_se=", reference_se)
                # print("")

                # Find *part_name_se* from *component_se*:
                part_name_se = Kicad.se_find(component_se, "comp", "value")

                # Suprisingly tedious, extract *part_name* as a string:
                if isinstance(part_name_se[1], Symbol):
                    part_name = part_name_se[1].value()
                elif isinstance(part_name_se[1], int):
                    part_name = str(part_name_se[1])
                elif isinstance(part_name_se[1], float):
                    part_name = str(part_name_se[1])
                elif isinstance(part_name_se[1], str):
                    part_name = part_name_se[1]
                else:
                    assert False, "strange part_name: {0}". \
                      format(part_name_se[1])

                # Strip *comment* out of *part_name* if it exists:
                comment = ""
                colon_index = part_name.find(':')
                if colon_index >= 0:
                    comment = part_name[colon_index + 1:]
                    part_name = part_name[0:colon_index]

                # Now see if we have a match for *part_name* in *database*:
                project_part = project.project_part_find(part_name)

                # We have a match; create the *pose_part*:
                pose_part = bom.PosePart(project, project_part, reference, comment)
                project.pose_part_append(pose_part)

                # Ignore footprints for now:
                if False:
                    # Grab *kicad_footprint* from *project_part*:
                    kicad_footprint = project_part.kicad_footprint
                    assert isinstance(kicad_footprint, str)

                    # Grab *footprint_se* from *component_se* (if it exists):
                    footprint_se = Kicad.se_find(component_se, "comp", "footprint")
                    # print("footprint_se=", footprint_se)
                    # print("Part[{0}]:'{1}' '{2}' changed={3}".format(
                    #    component_index, part_name, kicad_footprint, net_file_changed))

                    # Either add or update the footprint:
                    if footprint_se is None:
                        # No footprint in the .net file; just add one:
                        component_se.append(
                          [Symbol("footprint"), Symbol("common:" + kicad_footprint)])
                        print("Part {0}: Adding binding to footprint '{1}'".
                              format(part_name, kicad_footprint))
                        net_file_changed = True
                    else:
                        # We have a footprint in .net file:
                        previous_footprint = footprint_se[1].value()
                        previous_split = previous_footprint.split(':')
                        current_split = kicad_footprint.split(':')
                        assert len(previous_split) > 0
                        assert len(current_split) > 0
                        if len(current_split) == 2:
                            # *kicad_footprint* has an explicit library,
                            # so we can just use it and ignore
                            # *previous_footprint*:
                            new_footprint = kicad_footprint
                        elif len(current_split) == 1 and len(previous_split) == 2:
                            # *kicad_footprint* does not specify a library,
                            # but the *previous_footprint* does.  We build
                            # *new_foot_print* using the *previous_footprint*
                            # library and the rest from *kicad_footprint*:
                            new_footprint = \
                              previous_split[0] + ":" + kicad_footprint
                            # print("new_footprint='{0}'".format(new_footprint))
                        elif len(current_split) == 1:
                            new_footprint = "common:" + kicad_footprint
                        else:
                            assert False, ("previous_slit={0} current_split={1}".
                                           format(previous_split, current_split))
    
                        # Only do something if it changed:
                        if previous_footprint != new_footprint:
                            # Since they changed, update in place:
                            # if isinstance(project_part, AliasPart):
                            #        print("**AliasPart.footprint={0}".
                            #          format(project_part.kicad_footprint))
                            print("Part '{0}': Footprint changed from '{1}' to '{2}'".
                                  format(part_name, previous_footprint, new_footprint))
                            footprint_se[1] = Symbol(new_footprint)
                            net_file_changed = True

            success = True

            # Write out updated *net_file_name* if *net_file_changed*:
            if net_file_changed:
                print("Updating '{0}' with new footprints".
                      format(net_file_name))
                net_file = open(net_file_name, "wa")
                # sexpdata.dump(net_se, net_file)
                net_se_string = sexpdata.dumps(net_se)
                # sexpdata.dump(net_se, net_file)

                # Now use some regular expressions to improve formatting to be more like
                # what KiCad outputs:
                net_se_string = re.sub(" \\(design ", "\n  (design ", net_se_string)

                # Sheet part of file:
                net_se_string = re.sub(" \\(sheet ",       "\n    (sheet ",         net_se_string)
                net_se_string = re.sub(" \\(title_block ", "\n      (title_block ", net_se_string)
                net_se_string = re.sub(" \\(title ",       "\n        (title ",     net_se_string)
                net_se_string = re.sub(" \\(company ",     "\n        (company ",   net_se_string)
                net_se_string = re.sub(" \\(rev ",         "\n        (rev ",       net_se_string)
                net_se_string = re.sub(" \\(date ",        "\n        (date ",      net_se_string)
                net_se_string = re.sub(" \\(source ",      "\n        (source ",    net_se_string)
                net_se_string = re.sub(" \\(comment ",     "\n        (comment ",   net_se_string)

                # Components part of file:
                net_se_string = re.sub(" \\(components ", "\n  (components ",    net_se_string)
                net_se_string = re.sub(" \\(comp ",       "\n    (comp ",        net_se_string)
                net_se_string = re.sub(" \\(value ",      "\n      (value ",     net_se_string)
                net_se_string = re.sub(" \\(footprint ",  "\n      (footprint ", net_se_string)
                net_se_string = re.sub(" \\(libsource ",  "\n      (libsource ", net_se_string)
                net_se_string = re.sub(" \\(sheetpath ",  "\n      (sheetpath ", net_se_string)
                net_se_string = re.sub(" \\(path ",       "\n      (path ",      net_se_string)
                net_se_string = re.sub(" \\(tstamp ",     "\n      (tstamp ",    net_se_string)

                # Library parts part of file
                net_se_string = re.sub(" \\(libparts ",    "\n  (libparts ",    net_se_string)
                net_se_string = re.sub(" \\(libpart ",     "\n    (libpart ",   net_se_string)
                net_se_string = re.sub(" \\(description ", "\n      (description ",  net_se_string)
                net_se_string = re.sub(" \\(fields ",      "\n      (fields ",  net_se_string)
                net_se_string = re.sub(" \\(field ",       "\n        (field ", net_se_string)
                net_se_string = re.sub(" \\(pins ",        "\n      (pins ",    net_se_string)
                # net_se_string = re.sub(" \\(pin ",         "\n        (pin ",   net_se_string)

                # Network portion of file:
                net_se_string = re.sub(" \\(nets ", "\n  (nets ", net_se_string)
                net_se_string = re.sub(" \\(net ",  "\n    (net ", net_se_string)
                net_se_string = re.sub(" \\(node ", "\n      (node ", net_se_string)

                # General substitutions:
                # net_se_string = re.sub(" \\;", ";", net_se_string)
                # net_se_string = re.sub(" \\.", ".", net_se_string)

                net_file.write(net_se_string)
                net_file.close()

        # Wrap up any requested *tracing* and return *success*:
        if tracing is not None:
            print(f"{tracing}<=Kicad.net_file_read(*, '{net_file_name}', *)=>{success}")
        return success

    # "se" stands for LISP "S Expression":
    @staticmethod
    def se_find(se, base_name, key_name):
        """ {}: Find *key_name* in *se* and return its value. """

        # *se* is a list of the form:
        #
        #        [base_name, [key1, value1], [key2, value2], ..., [keyN, valueN]]
        #
        # This routine searches through the *[keyI, valueI]* pairs
        # and returnts the *valueI* that corresponds to *key_name*.

        # Check argument types:
        assert isinstance(se, list)
        assert isinstance(base_name, str)
        assert isinstance(key_name, str)

        # Do some sanity checking:
        size = len(se)
        assert size > 0
        assert se[0] == Symbol(base_name)

        result = None
        key_symbol = Symbol(key_name)
        for index in range(1, size):
            sub_se = se[index]
            if len(sub_se) > 0 and sub_se[0] == key_symbol:
                result = sub_se
                break
        return result

