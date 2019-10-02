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
from bom_manager.tracing import trace
import csv
import os
import re
import sexpdata                 # type: ignore  # (LISP)S-EXPression DATA package
from sexpdata import Symbol     # (LISP) S-expression Symobl
from typing import Any, List, TextIO

# cad_get():
@trace(1)
def cad_get(tracing: str = "") -> "Kicad":
    # Create the *kicad* object and return it:
    kicad: Kicad = Kicad()
    return kicad


# Kicad:
class Kicad(bom.Cad):

    # Kicad.__init__():
    @trace(1)
    def __init__(self, tracing: str = "") -> None:
        # Initialize the super class of the *Kicad* object (i.e. *self*):
        super().__init__("Kicad")

    # Kicad.__str__():
    def __str__(self) -> str:
        return "Kicad('Kicad')"

    # Kicad.altium_csv_read():
    @trace(1)
    def altium_csv_read(self, csv_file_name: str, project: bom.Project, tracing: str = "") -> bool:
        # ...
        success: bool = False
        csv_file: TextIO
        with open(csv_file_name, encoding="iso-8859-1") as csv_file:
            csv_rows: List[List[str]] = list(csv.reader(csv_file, delimiter=",", quotechar='"'))
            actual_headers: List[str] = csv_rows[0]
            if True:
                desired_headers: List[str] = [
                    "Line #", "Name", "Description", "Designator", "Quantity", "TargetPrice",
                    "Manufacturer 1", "Manufacturer Part Number 1", "Manufacturer Lifecycle 1",
                    "Supplier 1", "Supplier Part Number 1", "Supplier Unit Price 1",
                    "Supplier Subtotal 1"]
                index: int
                for index, desired_header in enumerate(desired_headers):
                    assert desired_header == actual_headers[index], f"index={index}"
                assert (actual_headers == desired_headers), (f"Got {actual_headers} "
                                                             f"instead of {desired_headers}")
                # project_parts = list()
                row: List[str]
                for index, row in enumerate(csv_rows[2:]):
                    # Unpack *row* and further split and strip *refs_text* into *refs*:
                    line_number: str
                    name: str
                    description: str
                    designators_text: str
                    quantity: str
                    line_number, name, description, designators_text, quantity = row[:5]
                    designators: List[str] = designators_text.split(",")
                    designators = [designator.strip() for designator in designators]
                    if tracing:
                        print(f"{tracing}Row[{index}]: "
                              f"{quantity}\t'{name}'\t{designators_text}")

                    # Lookup/create the *project_part* associated with *value*:
                    project_part: bom.ProjectPart = project.project_part_find(name)

                    # Create one *pose_part* for each *reference* in *references*:
                    for designator in designators:
                        pose_part: bom.PosePart = bom.PosePart(project,
                                                               project_part, designator, "")
                        project.pose_part_append(pose_part)

                    # Ignore footprints for now:
                    success = True
            else:
                assert False, (f"Could not succesfully read '{csv_file_name}'")
        return success

    # Kicad.csv_file_read():
    @trace(1)
    def bom_csv_grouped_by_value_with_fp_read(self, csv_file_name: str, project: bom.Project,
                                              tracing: str = "") -> bool:
        # ...
        success: bool = False
        csv_file: TextIO
        with open(csv_file_name) as csv_file:
            csv_rows = list(csv.reader(csv_file, delimiter=",", quotechar='"'))
            assert csv_rows[0][0] == "Source:"
            # source = csv_rows[0][1]
            assert csv_rows[1][0] == "Date:"
            # date = csv_rows[1],[1]
            assert csv_rows[2][0] == "Tool:"
            # tool = csv_rows[2][1]
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
                # project_parts = list()
                for index, row in enumerate(csv_rows[6:6+component_count]):
                    # Unpack *row* and further split and strip *refs_text* into *refs*:
                    references_text, quantity, part_name, component_name, footprint = row[:5]
                    references = references_text.split(",")
                    references = [reference.strip() for reference in references]
                    if tracing:
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

        return success

    # Kicad.file_read():
    @trace(1)
    def file_read(self, file_name: str, project: bom.Project, tracing: str = "") -> bool:
        # Dispatach on the *file_name* suffix:
        kicad: Kicad = self
        success: bool = False
        assert os.path.isfile(file_name), f"File '{file_name}' does not exist"
        if file_name.endswith(".cmp"):
            # success = kicad.cmp_file_read(file_name, project)
            assert False, ".cmp files are no longer supported."
        elif file_name.endswith(".csv"):
            try:
                success = kicad.altium_csv_read(file_name, project)
            except AssertionError:
                try:
                    success = kicad.bom_csv_grouped_by_value_with_fp_read(file_name, project)
                except AssertionError:
                    success = False
        elif file_name.endswith(".net"):
            success = kicad.net_file_read(file_name, project)

        return success

    # Kicad.net_file_read():
    @trace(1)
    def net_file_read(self, net_file_name: str, project: bom.Project, tracing: str = "") -> bool:
        """ Read in net file for the project object.
        """
        # Prevent accidental double of *project* (i.e. *self*):
        # kicad = self
        pose_parts: List[bom.PosePart] = project.all_pose_parts
        assert len(pose_parts) == 0

        # Process *net_file_name* adding footprints as needed:
        success: bool = False
        # errors = 0
        net_file: TextIO
        with open(net_file_name, "r") as net_file:
            # Read contents of *net_file_name* in as a string *net_text*:
            net_text: str = net_file.read()
            if tracing:
                print(f"{tracing}Read in file '{net_file_name}'")

            # Parse *net_text* into *net_se* (i.e. net S-expression):
            net_se: List[Any] = sexpdata.loads(net_text)
            # print("\nsexpedata.dumps=", sexpdata.dumps(net_se))
            # print("")
            # print("net_se=", net_se)
            # print("")

            # Visit each *component_se* in *net_se*:
            net_file_changed = False
            components_se: List[Any] = Kicad.se_find(net_se, "export", "components")

            # Each component has the following form:
            #
            #        (comp
            #          (ref SW123)
            #          (footprint nickname:NAME)              # May not be present
            #          (libsource ....)
            #          (sheetpath ....)
            #          (tstamp xxxxxxxx))
            # print("components=", components_se)
            component_index: int
            component_se: List[Any]
            for component_index, component_se in enumerate(components_se[1:]):
                # print("component_se=", component_se)
                # print("")

                # Grab the *reference* from *component_se*:
                reference_se: List[Any] = Kicad.se_find(component_se, "comp", "ref")
                reference: Any = reference_se[1].value()
                # print("reference_se=", reference_se)
                # print("")

                # Find *part_name_se* from *component_se*:
                part_name_se: List[Any] = Kicad.se_find(component_se, "comp", "value")

                # Suprisingly tedious, extract *part_name* as a string:
                part_name: str = "??"
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
                colon_index: int = part_name.find(':')
                if colon_index >= 0:
                    comment: str = part_name[colon_index + 1:]
                    part_name = part_name[0:colon_index]

                # Now see if we have a match for *part_name* in *database*:
                project_part: bom.ProjectPart = project.project_part_find(part_name)

                # We have a match; create the *pose_part*:
                pose_part: bom.PosePart = bom.PosePart(project, project_part, reference, comment)
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
                with open(net_file_name, "w") as net_file:
                    # sexpdata.dump(net_se, net_file)
                    net_se_string = sexpdata.dumps(net_se)
                    # sexpdata.dump(net_se, net_file)

                    # Now use some regular expressions to improve formatting to be more like
                    # what KiCad outputs:
                    net_se_string = re.sub(" \\(design ",
                                           "\n  (design ", net_se_string)

                    # Sheet part of file:
                    net_se_string = re.sub(" \\(sheet ",
                                           "\n    (sheet ", net_se_string)
                    net_se_string = re.sub(" \\(title_block ",
                                           "\n      (title_block ", net_se_string)
                    net_se_string = re.sub(" \\(title ",
                                           "\n        (title ", net_se_string)
                    net_se_string = re.sub(" \\(company ",
                                           "\n        (company ", net_se_string)
                    net_se_string = re.sub(" \\(rev ",
                                           "\n        (rev ", net_se_string)
                    net_se_string = re.sub(" \\(date ",
                                           "\n        (date ", net_se_string)
                    net_se_string = re.sub(" \\(source ",
                                           "\n        (source ", net_se_string)
                    net_se_string = re.sub(" \\(comment ",
                                           "\n        (comment ", net_se_string)

                # Components part of file:
                net_se_string = re.sub(" \\(components ",
                                       "\n  (components ", net_se_string)
                net_se_string = re.sub(" \\(comp ",
                                       "\n    (comp ", net_se_string)
                net_se_string = re.sub(" \\(value ",
                                       "\n      (value ", net_se_string)
                net_se_string = re.sub(" \\(footprint ",
                                       "\n      (footprint ", net_se_string)
                net_se_string = re.sub(" \\(libsource ",
                                       "\n      (libsource ", net_se_string)
                net_se_string = re.sub(" \\(sheetpath ",
                                       "\n      (sheetpath ", net_se_string)
                net_se_string = re.sub(" \\(path ",
                                       "\n      (path ", net_se_string)
                net_se_string = re.sub(" \\(tstamp ",
                                       "\n      (tstamp ", net_se_string)

                # Library parts part of file
                net_se_string = re.sub(" \\(libparts ",
                                       "\n  (libparts ", net_se_string)
                net_se_string = re.sub(" \\(libpart ",
                                       "\n    (libpart ", net_se_string)
                net_se_string = re.sub(" \\(description ",
                                       "\n      (description ",  net_se_string)
                net_se_string = re.sub(" \\(fields ",
                                       "\n      (fields ",  net_se_string)
                net_se_string = re.sub(" \\(field ",
                                       "\n        (field ", net_se_string)
                net_se_string = re.sub(" \\(pins ",
                                       "\n      (pins ", net_se_string)
                # net_se_string = re.sub(" \\(pin ",
                #                        "\n        (pin ", net_se_string)

                # Network portion of file:
                net_se_string = re.sub(" \\(nets ", "\n  (nets ", net_se_string)
                net_se_string = re.sub(" \\(net ",  "\n    (net ", net_se_string)
                net_se_string = re.sub(" \\(node ", "\n      (node ", net_se_string)

                # General substitutions:
                # net_se_string = re.sub(" \\;", ";", net_se_string)
                # net_se_string = re.sub(" \\.", ".", net_se_string)

                net_file.write(net_se_string)

        return success

    # "se" stands for LISP "S Expression":
    @staticmethod
    def se_find(se: List[Any], base_name: str, key_name: str) -> List[Any]:
        """ {}: Find *key_name* in *se* and return its value. """

        # *se* is a list of the form:
        #
        #        [base_name, [key1, value1], [key2, value2], ..., [keyN, valueN]]
        #
        # This routine searches through the *[keyI, valueI]* pairs
        # and returnts the *valueI* that corresponds to *key_name*.

        # Do some sanity checking:
        size: int = len(se)
        assert size > 0
        assert se[0] == Symbol(base_name)

        result: List[Any] = list()
        key_symbol: Symbol = Symbol(key_name)
        index: int
        for index in range(1, size):
            sub_se: List[Any] = se[index]
            if len(sub_se) > 0 and sub_se[0] == key_symbol:
                result = sub_se
                break
        return result
