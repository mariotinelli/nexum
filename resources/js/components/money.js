export function brlMask(value) {
    if (!value && value !== 0) return "";

    value = String(value);

    if (!value.includes(".") && !value.includes(",") && value.length > 1) {
        value = value.concat(".00");
    }

    if (value.includes(".") && value.split(".")[1].length === 1) {
        value = value.concat("0");
    }

    let numericValue = value.replace(/\D/g, "");

    if (!numericValue) return "";

    numericValue = numericValue.replace(/^0+/, "") || "0";

    let number = (Number(numericValue) / 100).toFixed(2);

    if (Number(number) > 99999999.99) {
        number = "99999999.99";
    }

    number = number.replace(".", ",");
    number = number.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

    return number;
}

export function usdMask(value) {
    if (!value && value !== 0) return "";

    let numericValue = String(value).replace(/\D/g, "");

    if (!numericValue) return "";

    numericValue = numericValue.replace(/^0+/, "") || "0";

    let number = (Number(numericValue) / 100).toFixed(2);

    if (Number(number) > 99999999.99) {
        number = "99999999.99";
    }

    number = number.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    return number;
}
