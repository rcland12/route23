#!/bin/bash

# Plex media naming verification script
# Supports both Movies and TV Shows
# 
# Movie format:
#   Directory: "Movie Title (YEAR) {imdb-ttXXXXXXX}"
#   Files: "Movie Title (YEAR) {imdb-ttXXXXXXX}.{ext}"
#
# TV Show format:
#   Show Directory: "Show Title (YEAR)"
#   Season Directory: "Season NN"
#   Episode Files: "Show Title (YEAR) - sNNeMM - Episode Title.{ext}"
#   Multi-episode: "Show Title (YEAR) - sNNeMM-MM - Episode Titles.{ext}"
#              or: "Show Title (YEAR) - sNNeMM-eMM - Episode Titles.{ext}"

MOVIES_DIR="/mnt/plex/Media/Movies"
TV_SHOWS_DIR="/mnt/plex/Media/TV Shows"
ERRORS_FOUND=0
VALID_COUNT=0
MODE="movie"

declare -a ERROR_MESSAGES

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --movie     Check movies (default)"
    echo "  -t, --tv        Check TV shows"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Check movies (default)"
    echo "  $0 -m           # Check movies"
    echo "  $0 -t           # Check TV shows"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--movie)
            MODE="movie"
            shift
            ;;
        -t|--tv)
            MODE="tv"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

validate_movie_directory_name() {
    local dir_name="$1"
    if [[ $dir_name =~ ^.*\ \([0-9]{4}\)\ \{imdb-tt[0-9]{7,}\}$ ]]; then
        return 0
    else
        return 1
    fi
}

extract_movie_components() {
    local dir_name="$1"
    local year=$(echo "$dir_name" | sed -n 's/.*(\([0-9]\{4\}\)).*/\1/p')
    local imdb_id=$(echo "$dir_name" | sed -n 's/.*{\(imdb-tt[0-9]\+\)}.*/\1/p')
    local title=$(echo "$dir_name" | sed 's/\s*(.*$//')

    echo "$title|$year|$imdb_id"
}

validate_subtitle_name() {
    local subtitle_file="$1"
    local expected_base="$2"

    if [ "$subtitle_file" = "${expected_base}.srt" ]; then
        return 0
    fi

    local escaped_base=$(printf '%s\n' "$expected_base" | sed 's/[[\.*^$()+?{|]/\\&/g')

    if [[ $subtitle_file =~ ^${escaped_base}\.[a-zA-Z]{2,}\.srt$ ]]; then
        return 0
    fi

    if [[ $subtitle_file =~ ^${escaped_base}\.(forced|sdh|cc)\.srt$ ]] || \
       [[ $subtitle_file =~ ^${escaped_base}\.[a-zA-Z]{2,}\.(forced|sdh|cc)\.srt$ ]]; then
        return 0
    fi

    return 1
}

validate_video_name() {
    local video_file="$1"
    local dir_name="$2"
    local extension="${video_file##*.}"

    local expected_single="${dir_name}.${extension}"
    if [ "$video_file" = "$expected_single" ]; then
        return 0
    fi

    if [[ $video_file =~ ^(.+)\ \([0-9]{4}\)\ -\ (disk|part)[0-9]+\ -\ \{imdb-tt[0-9]{7,}\}\.[a-zA-Z0-9]+$ ]]; then
        local base_part=$(echo "$video_file" | sed 's/ - \(disk\|part\)[0-9]\+ - {imdb-tt[0-9]\+}\.[a-zA-Z0-9]\+$//')
        if [ "$base_part" = "$(echo "$dir_name" | sed 's/ {imdb-tt[0-9]\+}$//')" ]; then
            return 0
        fi
    fi

    return 1
}

validate_tv_show_directory_name() {
    local dir_name="$1"
    if [[ $dir_name =~ ^.*\ \([0-9]{4}\)$ ]]; then
        return 0
    else
        return 1
    fi
}

validate_season_directory_name() {
    local dir_name="$1"
    if [[ $dir_name =~ ^Season\ [0-9]{2}$ ]]; then
        return 0
    else
        return 1
    fi
}

extract_tv_components() {
    local dir_name="$1"
    local year=$(echo "$dir_name" | sed -n 's/.*(\([0-9]\{4\}\)).*/\1/p')
    local title=$(echo "$dir_name" | sed 's/\s*(.*$//')
    
    echo "$title|$year"
}

validate_episode_name() {
    local episode_file="$1"
    local show_name="$2"
    local season_num="$3"
    local extension="${episode_file##*.}"
    local base_name="${episode_file%.*}"
    local escaped_show_name=$(printf '%s\n' "$show_name" | sed 's/[]\.|$(){}?+*^[]/\\&/g')
    local pattern_single="^${escaped_show_name} - s${season_num}e[0-9]{2,} - .+"
    local pattern_multi1="^${escaped_show_name} - s${season_num}e[0-9]{2,}-[0-9]{2,} - .+"
    local pattern_multi2="^${escaped_show_name} - s${season_num}e[0-9]{2,}-e[0-9]{2,} - .+"
    
    if [[ $base_name =~ ${pattern_single} ]] || \
       [[ $base_name =~ ${pattern_multi1} ]] || \
       [[ $base_name =~ ${pattern_multi2} ]]; then
        return 0
    else
        return 1
    fi
}

validate_tv_subtitle_name() {
    local subtitle_file="$1"
    local show_name="$2"
    local season_num="$3"
    local base_name="${subtitle_file%.srt}"
    local escaped_show_name=$(printf '%s\n' "$show_name" | sed 's/[]\.|$(){}?+*^[]/\\&/g')
    local pattern_single="^${escaped_show_name} - s${season_num}e[0-9]{2,} - .+"
    local pattern_multi1="^${escaped_show_name} - s${season_num}e[0-9]{2,}-[0-9]{2,} - .+"
    local pattern_multi2="^${escaped_show_name} - s${season_num}e[0-9]{2,}-e[0-9]{2,} - .+"
    
    if [[ $base_name =~ ${pattern_single} ]] || \
       [[ $base_name =~ ${pattern_multi1} ]] || \
       [[ $base_name =~ ${pattern_multi2} ]]; then
        return 0
    else
        return 1
    fi
}

verify_movies() {
    echo -e "${BLUE}Starting movie naming verification...${NC}"
    echo "Checking directory: $MOVIES_DIR"
    echo "Expected format: Movie Title (YEAR) {imdb-ttXXXXXXX}"
    echo "----------------------------------------"

    if [ ! -d "$MOVIES_DIR" ]; then
        echo -e "${RED}ERROR: Movies directory not found: $MOVIES_DIR${NC}"
        exit 1
    fi

    declare -a movie_dirs
    while IFS= read -r -d '' movie_dir; do
        movie_dirs+=("$movie_dir")
    done < <(find "$MOVIES_DIR" -maxdepth 1 -type d ! -path "$MOVIES_DIR" -print0)

    IFS=$'\n' sorted_dirs=($(printf '%s\n' "${movie_dirs[@]}" | sort))
    unset IFS

    for movie_dir in "${sorted_dirs[@]}"; do
        dir_name=$(basename "$movie_dir")

        echo -e "\n${YELLOW}Checking:${NC} $dir_name"

        if ! validate_movie_directory_name "$dir_name"; then
            echo -e "${RED}  ❌ INVALID DIRECTORY FORMAT${NC}"
            echo "     Expected: Title (YEAR) {imdb-ttXXXXXXX}"
            echo "     Note: IMDB ID should be at least 7 digits (tt1234567 or longer)"
            ERROR_MESSAGES+=("MOVIE: $dir_name - Invalid directory format (Expected: Title (YEAR) {imdb-ttXXXXXXX})")
            ((ERRORS_FOUND++))
            continue
        fi

        IFS='|' read -r title year imdb_id <<< "$(extract_movie_components "$dir_name")"

        video_files=()
        while IFS= read -r -d '' video_file; do
            video_files+=("$(basename "$video_file")")
        done < <(find "$movie_dir" -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mkv" -o -name "*.avi" -o -name "*.m4v" -o -name "*.mov" \) -print0)

        subtitle_files=()
        while IFS= read -r -d '' subtitle_file; do
            subtitle_files+=("$(basename "$subtitle_file")")
        done < <(find "$movie_dir" -maxdepth 1 -type f -name "*.srt" -print0)

        if [ ${#video_files[@]} -eq 0 ]; then
            echo -e "${RED}  ❌ NO VIDEO FILE FOUND${NC}"
            ERROR_MESSAGES+=("MOVIE: $dir_name - No video file found")
            ((ERRORS_FOUND++))
            continue
        fi

        video_naming_errors=0
        valid_video_files=0

        if [ ${#video_files[@]} -eq 1 ]; then
            video_file="${video_files[0]}"
            if validate_video_name "$video_file" "$dir_name"; then
                echo -e "${GREEN}  ✅ Video file correctly named${NC}"
                ((valid_video_files++))
            else
                echo -e "${RED}  ❌ VIDEO FILE NAME MISMATCH${NC}"
                video_extension="${video_file##*.}"
                echo "     Found:    $video_file"
                echo "     Expected: ${dir_name}.${video_extension}"
                echo "     Or multi-part format: ${dir_name%{*}- disk1 - ${dir_name##*{}.${video_extension}"
                ERROR_MESSAGES+=("MOVIE: $dir_name - Video file name mismatch: $video_file")
                ((video_naming_errors++))
            fi
        else
            echo -e "${YELLOW}  Multiple video files found (${#video_files[@]} files):${NC}"

            IFS=$'\n' sorted_files=($(sort <<<"${video_files[*]}"))
            unset IFS

            for video_file in "${sorted_files[@]}"; do
                if validate_video_name "$video_file" "$dir_name"; then
                    echo -e "     ${GREEN}✅${NC} $video_file"
                    ((valid_video_files++))
                else
                    echo -e "     ${RED}❌${NC} $video_file"
                    ERROR_MESSAGES+=("MOVIE: $dir_name - Invalid video file name: $video_file")
                    ((video_naming_errors++))
                fi
            done

            if [ $video_naming_errors -eq 0 ]; then
                echo -e "${GREEN}  ✅ All video files correctly named${NC}"
            fi
        fi

        if [ $video_naming_errors -gt 0 ]; then
            ((ERRORS_FOUND++))
        fi

        if [ ${#subtitle_files[@]} -gt 0 ]; then
            echo -e "     Found ${#subtitle_files[@]} subtitle file(s):"
            subtitle_errors=0

            IFS=$'\n' sorted_subtitles=($(sort <<<"${subtitle_files[*]}"))
            unset IFS

            for subtitle_file in "${sorted_subtitles[@]}"; do
                if validate_subtitle_name "$subtitle_file" "$dir_name"; then
                    echo -e "     ${GREEN}✅${NC} $subtitle_file"
                else
                    echo -e "     ${RED}❌${NC} $subtitle_file (invalid format)"
                    echo "        Expected formats: ${dir_name}.srt, ${dir_name}.en.srt, ${dir_name}.fr.srt, etc."
                    ERROR_MESSAGES+=("MOVIE: $dir_name - Invalid subtitle file name: $subtitle_file")
                    ((subtitle_errors++))
                fi
            done
            if [ $subtitle_errors -gt 0 ]; then
                ((ERRORS_FOUND++))
            fi
        fi

        if [ $video_naming_errors -eq 0 ]; then
            ((VALID_COUNT++))
        fi

    done
}

verify_tv_shows() {
    echo -e "${BLUE}Starting TV show naming verification...${NC}"
    echo "Checking directory: $TV_SHOWS_DIR"
    echo "Expected format:"
    echo "  Show: Show Title (YEAR)"
    echo "  Season: Season NN"
    echo "  Episode: Show Title (YEAR) - sNNeMM - Episode Title.ext"
    echo "  Multi-episode: Show Title (YEAR) - sNNeMM-MM - Episodes.ext"
    echo "             or: Show Title (YEAR) - sNNeMM-eMM - Episodes.ext"
    echo "----------------------------------------"

    if [ ! -d "$TV_SHOWS_DIR" ]; then
        echo -e "${RED}ERROR: TV Shows directory not found: $TV_SHOWS_DIR${NC}"
        exit 1
    fi

    declare -a show_dirs
    while IFS= read -r -d '' show_dir; do
        show_dirs+=("$show_dir")
    done < <(find "$TV_SHOWS_DIR" -maxdepth 1 -type d ! -path "$TV_SHOWS_DIR" -print0)

    IFS=$'\n' sorted_dirs=($(printf '%s\n' "${show_dirs[@]}" | sort))
    unset IFS

    for show_dir in "${sorted_dirs[@]}"; do
        show_name=$(basename "$show_dir")

        echo -e "\n${YELLOW}Checking Show:${NC} $show_name"

        if ! validate_tv_show_directory_name "$show_name"; then
            echo -e "${RED}  ❌ INVALID SHOW DIRECTORY FORMAT${NC}"
            echo "     Expected: Show Title (YEAR)"
            ERROR_MESSAGES+=("TV SHOW: $show_name - Invalid show directory format (Expected: Show Title (YEAR))")
            ((ERRORS_FOUND++))
            continue
        fi

        IFS='|' read -r title year <<< "$(extract_tv_components "$show_name")"

        season_dirs=()
        while IFS= read -r -d '' season_dir; do
            season_dirs+=("$season_dir")
        done < <(find "$show_dir" -maxdepth 1 -type d ! -path "$show_dir" -print0)

        if [ ${#season_dirs[@]} -eq 0 ]; then
            echo -e "${RED}  ❌ NO SEASON DIRECTORIES FOUND${NC}"
            ERROR_MESSAGES+=("TV SHOW: $show_name - No season directories found")
            ((ERRORS_FOUND++))
            continue
        fi

        IFS=$'\n' sorted_seasons=($(printf '%s\n' "${season_dirs[@]}" | sort))
        unset IFS

        show_has_errors=0

        for season_dir in "${sorted_seasons[@]}"; do
            season_name=$(basename "$season_dir")

            if ! validate_season_directory_name "$season_name"; then
                echo -e "${RED}  ❌ INVALID SEASON DIRECTORY: $season_name${NC}"
                echo "     Expected: Season NN (e.g., Season 01, Season 02)"
                ERROR_MESSAGES+=("TV SHOW: $show_name - Invalid season directory: $season_name")
                ((ERRORS_FOUND++))
                show_has_errors=1
                continue
            fi

            season_num=$(echo "$season_name" | sed 's/Season //')

            video_files=()
            while IFS= read -r -d '' video_file; do
                video_files+=("$(basename "$video_file")")
            done < <(find "$season_dir" -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mkv" -o -name "*.avi" -o -name "*.m4v" -o -name "*.mov" \) -print0)

            subtitle_files=()
            while IFS= read -r -d '' subtitle_file; do
                subtitle_files+=("$(basename "$subtitle_file")")
            done < <(find "$season_dir" -maxdepth 1 -type f -name "*.srt" -print0)

            if [ ${#video_files[@]} -eq 0 ]; then
                echo -e "${RED}  ❌ $season_name: NO VIDEO FILES FOUND${NC}"
                ERROR_MESSAGES+=("TV SHOW: $show_name/$season_name - No video files found")
                ((ERRORS_FOUND++))
                show_has_errors=1
                continue
            fi

            echo -e "  ${BLUE}$season_name:${NC} ${#video_files[@]} episode(s)"

            episode_errors=0
            IFS=$'\n' sorted_episodes=($(sort <<<"${video_files[*]}"))
            unset IFS

            for episode_file in "${sorted_episodes[@]}"; do
                if validate_episode_name "$episode_file" "$show_name" "$season_num"; then
                    echo -e "     ${GREEN}✅${NC} $episode_file"
                else
                    echo -e "     ${RED}❌${NC} $episode_file"
                    echo "        Expected formats:"
                    echo "          Single: $show_name - s${season_num}eNN - Episode Title.ext"
                    echo "          Multi:  $show_name - s${season_num}eNN-NN - Episode Titles.ext"
                    echo "          Multi:  $show_name - s${season_num}eNN-eNN - Episode Titles.ext"
                    ERROR_MESSAGES+=("TV SHOW: $show_name/$season_name - Invalid episode name: $episode_file")
                    ((episode_errors++))
                fi
            done

            if [ ${#subtitle_files[@]} -gt 0 ]; then
                subtitle_errors=0
                IFS=$'\n' sorted_subtitles=($(sort <<<"${subtitle_files[*]}"))
                unset IFS

                for subtitle_file in "${sorted_subtitles[@]}"; do
                    if validate_tv_subtitle_name "$subtitle_file" "$show_name" "$season_num"; then
                        echo -e "     ${GREEN}✅${NC} $subtitle_file (subtitle)"
                    else
                        echo -e "     ${RED}❌${NC} $subtitle_file (invalid subtitle format)"
                        echo "        Expected formats:"
                        echo "          Single: $show_name - s${season_num}eNN - Episode Title[.lang].srt"
                        echo "          Multi:  $show_name - s${season_num}eNN-NN - Episode Titles[.lang].srt"
                        echo "          Multi:  $show_name - s${season_num}eNN-eNN - Episode Titles[.lang].srt"
                        ERROR_MESSAGES+=("TV SHOW: $show_name/$season_name - Invalid subtitle name: $subtitle_file")
                        ((subtitle_errors++))
                    fi
                done

                if [ $subtitle_errors -gt 0 ]; then
                    ((ERRORS_FOUND++))
                    show_has_errors=1
                fi
            fi

            if [ $episode_errors -gt 0 ]; then
                ((ERRORS_FOUND++))
                show_has_errors=1
            fi

        done

        if [ $show_has_errors -eq 0 ]; then
            ((VALID_COUNT++))
        fi

    done
}

if [ "$MODE" = "movie" ]; then
    verify_movies
    item_type="movies"
else
    verify_tv_shows
    item_type="TV shows"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}VERIFICATION SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Valid $item_type: $VALID_COUNT${NC}"
echo -e "${RED}Issues found: $ERRORS_FOUND${NC}"

if [ $ERRORS_FOUND -gt 0 ]; then
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}ERROR DETAILS${NC}"
    echo -e "${BLUE}========================================${NC}"
    for error in "${ERROR_MESSAGES[@]}"; do
        echo -e "${RED}❌${NC} $error"
    done
fi

if [ $ERRORS_FOUND -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All $item_type are correctly named!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Please review and fix the issues listed above.${NC}"
    exit 1
fi
