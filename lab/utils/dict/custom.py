from termcolor import colored as ced

from utils.log.custom import txtLog, errorLine

from utils.dict_utils import get_list_signature
from utils.terminal_utils import terminalTitle
from utils.cmd_format import cmd_blink

from constants.project import PRE_LOG_ERR, PRE_LOG_INFO, SUP_LINE
from constants.terminal import PRE_CMD_INFO, PRE_CMD_MIDDLE_DOT, PRE_CMD_MIDDLE_DOT_LIST


def listSignature(_listDict) -> None:
    """
    Print the list information on the screen.
    """
    try:
        #> attempt to get list information from the list page.
        listSign = get_list_signature(_listDict)

        terminalTitle(f"{_listDict['process_state']} Process: @{_listDict['list_owner']}.")

        signList = [
            f"\n{PRE_CMD_INFO}Process State: {cmd_blink(_listDict['process_state'],'green')}",
            SUP_LINE,
            f"{PRE_CMD_INFO}{ced('List info;', color='yellow')}",
            f"{PRE_CMD_MIDDLE_DOT}List by {ced(listSign['list_by'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Updated: {ced(listSign['list_update_time_humanize'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Published: {ced(listSign['list_publication_time_humanize'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List title: {ced(listSign['list_title'], 'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Filters;",
            f"{PRE_CMD_MIDDLE_DOT_LIST}Filtered as {ced(listSign['list_selected_decade_year'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Filtered as {ced(listSign['list_selected_genre'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Movies sorted by {ced(listSign['list_selected_sort_by'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List hash: {ced(_listDict['list_run_time'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Sayfa sayısı: {ced(listSign['list_last_page'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Number of movies: {ced(listSign['list_movie_count'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List domain name: {ced(_listDict['list_domain_name'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List URL: {ced(_listDict['list_url'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Process URL: {ced(_listDict['list_detail_url'],'blue', attrs=['bold'])}"
        ]

        print('\n'.join(signList))
        txtLog(f"{PRE_LOG_INFO}List's signature print success.")
    except Exception as e:
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}List signature print error.')