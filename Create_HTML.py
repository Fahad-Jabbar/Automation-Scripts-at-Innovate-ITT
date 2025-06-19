import json
import logging
import sys
import os

logger = None


def init_logger():
    numeric_level = getattr(logging, "DEBUG", None)
    # noinspection PyArgumentList
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(levelname)-8s %(message)s', level=numeric_level,
                        datefmt='%Y-%m-%d %H:%M:%S')
    return logging.getLogger('HAT_POST')

def add_current_variant(curr_no, col_size, width = "100%"):
    current_variant_image = variants_info[str(curr_no)]["variant_image_path"]
    current_variant_image_data_dir = os.path.join(data_dir, os.path.basename(current_variant_image))
    os.system(f'cp -r {current_variant_image} {current_variant_image_data_dir}')
    config = {
        "class": col_size,
        "layout": {
            "mode": "image",
            "width": width,
            "src": current_variant_image_data_dir,
            "text": variants_info[str(curr_no)]["variant_name"] + " (" + variants_info[str(curr_no)]["variant_description"] + ")",
            "zoom": 300
        }
    }
    html_config[1]["layout"]["cols"].append(config)


def add_base_variant(base_no, col_size, width = "100%"):
    base_variant_image = variants_info["base_variants"][str(base_no)]["variant_image_path"]
    base_variant_image_data_dir = os.path.join(data_dir, os.path.basename(base_variant_image))
    os.system(f'cp -r {base_variant_image} {base_variant_image_data_dir}')
    config = {
        "class": col_size,
        "layout": {
            "mode": "image",
            "width": width,
            "src": base_variant_image_data_dir,
            "text": variants_info["base_variants"][str(base_no)]["variant_name"] + " (" + variants_info["base_variants"][str(base_no)]["variant_description"] + ")",
            "zoom": 300
        }
    }
    html_config[0]["layout"]["cols"].append(config)

def copy_variants_images(current_variant_numbers, last_current_variant_index):
    count = variants_info["current_variants_count"]
    number_of_current_variants = len(count.split(','))
    count = variants_info["base_variants"]["count"]
    if count == "0":
        number_of_base_variants = 0
    else:
        number_of_base_variants = len(count.split(','))
    
    cmd = f'cp -r {assets_for_html} {working_dir}'
    os.system(cmd)
    os.system(f'mkdir {data_dir}')
    if not os.path.exists(f'{assets_dir}') or not os.path.exists(f'{data_dir}'):
        logger.error(f"{data_dir} or {assets_dir} could not be created")
    
    if number_of_current_variants == 1:
        add_current_variant("1", "col-md-12", "50%")
    else:
        for no in range(1, number_of_current_variants + 1):
            add_current_variant(no, "col-md-6")
    
    if number_of_base_variants == 1:
        add_base_variant("1", "col-md-12", "50%")
    else:
        for no in range(1, number_of_base_variants + 1):
            add_base_variant(no, "col-md-6")

    outfile = variants_info[last_current_variant_index]["variant_auswertung_dir"] + os.path.sep + '{{Assembly-Parameters.current_variant_type}}' + '_HAT_LDAS_' + "_".join(current_variant_numbers)
    return outfile


def update_variants_configs():
    count = variants_info["current_variants_count"]
    number_of_current_variants = len(count.split(','))
    count = variants_info["base_variants"]["count"]
    if count == "0":
        number_of_base_variants = 0
    else:
        number_of_base_variants = len(count.split(','))
    current_variant_numbers = []
    for curr_no in range(1, number_of_current_variants + 1):
        number = variants_info[str(curr_no)]["variant_number"]
        name =  variants_info[str(curr_no)]["variant_name"]
        auswertung_dir =  variants_info[str(curr_no)]["variant_auswertung_dir"]
        variant_dict = {
            "number": number,
            "name": name,
            "color": current_variants_colors[curr_no - 1],
            "path": auswertung_dir
        }
        current_variant_numbers.append(number)
        variants_config.append(variant_dict)
    last_current_variant_index = str(curr_no)

    for base_no in range(1, number_of_base_variants + 1):
        number = variants_info["base_variants"][str(base_no)]["variant_number"]
        name =  variants_info["base_variants"][str(base_no)]["variant_name"]
        auswertung_dir =  variants_info["base_variants"][str(base_no)]["variant_auswertung_dir"]
        variant_dict = {
            "number": number,
            "name": name,
            "color": base_variants_colors[base_no - 1],
            "path": auswertung_dir
        }
        variants_config.append(variant_dict)

    paths = {
        "last_variant_auswertung": variants_info[last_current_variant_index]["variant_auswertung_dir"]
    }
    with open("{{HTML_Creation.useroutput}}", 'w') as outfile:
        json.dump(paths, outfile)
    
    outfile = copy_variants_images(current_variant_numbers, last_current_variant_index)
    return outfile, last_current_variant_index


def create_json_data():
    with open(variants_json, 'w') as f:
        json.dump(variants_config, f)

    os.system(f'cd {working_dir}')
    for html_type in html_types:
        logger.info(f"Creating json data for {html_type}")
        cmd = f"/proj/fem-sup/AUSTAUSCH/simuspace/suspython/python {json_creation_script} -i {variants_json} -t {html_type} -z {ziele_path} -o {html_type + '.json'}"
        logger.info(f"Command to be executed {cmd}")
        os.system(cmd)
        if os.path.isfile("{{Job.WorkingDir}}" + os.path.sep + html_type + '.json'):
            logger.info(f"{html_type + '.json'} created successfully")
        else:
            logger.error(f"json creation script failed. Did not created json data for {html_type + '.json'}")


def create_html_config():
    for config in html_config:
        if config['layout']['mode'] == 'plotly':
            if config['subtitle'] == 'vorne X':
                with open(working_dir + os.path.sep + 'LDAS_vorne_X.json') as json_file:
                    data = json.load(json_file)
                config['layout']['json'] = data
            elif config['subtitle'] == 'vorne Y':
                with open(working_dir + os.path.sep + 'LDAS_vorne_Y.json') as json_file:
                    data = json.load(json_file)
                config['layout']['json'] = data
            elif config['subtitle'] == 'vorne Z':
                with open(working_dir + os.path.sep + 'LDAS_vorne_Z.json') as json_file:
                    data = json.load(json_file)
                config['layout']['json'] = data
            elif config['subtitle'] == 'hinten X':
                with open(working_dir + os.path.sep + 'LDAS_hinten_X.json') as json_file:
                    data = json.load(json_file)
                config['layout']['json'] = data
            elif config['subtitle'] == 'hinten Y':
                with open(working_dir + os.path.sep + 'LDAS_hinten_Y.json') as json_file:
                    data = json.load(json_file)
                config['layout']['json'] = data
            elif config['subtitle'] == 'hinten Z':
                with open(working_dir + os.path.sep + 'LDAS_hinten_Z.json') as json_file:
                    data = json.load(json_file)
                config['layout']['json'] = data
            else:
                logger.error(f"Wrong subtitle {config['subtitle']} in json configuration for html")

    with open(html_config_file, 'w') as f:
        json.dump(html_config, f)
 

def make_html(last_current_variant_index): 
    logger.info(f"Creating HTML data")
    cmd = f"/proj/fem-sup/AUSTAUSCH/simuspace/suspython/python {html_creation_script} -c {html_config_file} -a {assets_dir} -o {outfile}"
    os.system(cmd)
    logger.info(f"Command to be executed {cmd}")

    if os.path.isfile(outfile + '.zip') and os.path.isfile(outfile + '.json'):
        logger.info(f"{outfile + '.zip'} and {outfile + '.json'} created successfully")
    else:
        logger.error(f"HTML creation script failed. Did not created {outfile + '.zip'} or {outfile + '.json'}")

    os.system(f'chmod -R 777 {variants_info[last_current_variant_index]["variant_auswertung_dir"]}')

def prepare_html_sus(outfile):
    fh=open("susimport.json","w")
    x = dict()
    html_json = os.path.basename(outfile) + '.json'
    x['Html'] = [html_json]
    json.dump(x,fh)
    fh.close()

if __name__ == "__main__":

    logger = init_logger()
    html_config = [
        {
            "title": "HAT Base",
            "subtitle": "{{Assembly-Parameters.current_variant_type}}",
            "layout": {
                "mode": "grid",
                "cols": []
            }
        },
        {
            "title": "HAT Current",
            "subtitle": "{{Assembly-Parameters.current_variant_type}}",
            "layout": {
                "mode": "grid",
                "cols": []
            }
        },
        {
            "title": "HAT LDAS Bewertung",
            "subtitle": "vorne X",
            "layout": {
                "mode": "plotly",
                "json": {}
            }
        },
        {
            "title": "HAT LDAS Bewertung",
            "subtitle": "vorne Y",
            "layout": {
                "mode": "plotly",
                "json": {}
            }
        },
        {
            "title": "HAT LDAS Bewertung",
            "subtitle": "vorne Z",
            "layout": {
                "mode": "plotly",
                "json": {}
            }
        },
        {
            "title": "HAT LDAS Bewertung",
            "subtitle": "hinten X",
            "layout": {
                "mode": "plotly",
                "json": {}
            }
        },
        {
            "title": "HAT LDAS Bewertung",
            "subtitle": "hinten Y",
            "layout": {
                "mode": "plotly",
                "json": {}
            }
        },
        {
            "title": "HAT LDAS Bewertung",
            "subtitle": "hinten Z",
            "layout": {
                "mode": "plotly",
                "json": {}
            }
        }
    ]
    variants_config = []
    variants_info = {{Pre_Processing.useroutput}}
    json_creation_script = '{{Assembly-Parameters.json_creation_script}}'
    html_creation_script = '{{Assembly-Parameters.html_creation_script}}'
    variants_json = "{{Job.WorkingDir}}" + os.path.sep + "variants.json"
    ziele_path = os.path.join('{{Assembly-Parameters.ziele}}', 'HAT_' + '{{Assembly-Parameters.current_variant_type}}', 'LDAS')
    html_types = ['LDAS_vorne_X', 'LDAS_vorne_Y', 'LDAS_vorne_Z', 'LDAS_hinten_X', 'LDAS_hinten_Y', 'LDAS_hinten_Z']
    working_dir = '{{Job.WorkingDir}}'
    html_config_file = os.path.join("{{Job.WorkingDir}}", 'html_config.json')
    assets_for_html = "{{Assembly-Parameters.assets_for_html}}"
    assets_dir = os.path.join(working_dir, os.path.basename(assets_for_html))
    data_dir = os.path.join(working_dir, "data")
    base_variants_colors = "{{Assembly-Parameters.base_variants_colors}}".split(",")
    current_variants_colors =  "{{Assembly-Parameters.current_variants_colors}}".split(",")
    
    outfile, last_current_variant_index = update_variants_configs()

    create_json_data()

    create_html_config()

    make_html(last_current_variant_index)

    prepare_html_sus(outfile)