/**
 * (c) 2024 Alberto Morón Hernández
 */

// `/welcome/` - onboarding flow
export function onboardingFormState(
    name,
    depositAmount,
    tenancyStartDateStr,
    tenancyEndDateStr,
) {
    return {
        fields: {
            name: name, // string
            depositAmount: depositAmount, // number
            tenancyStartDate: tenancyStartDateStr, // string
            tenancyEndDate: tenancyEndDateStr, // string
        },
        errors: {
            name: { isInvalid: false },
            depositAmount: { tooSmall: false },
            tenancyStartDate: { datesInWrongOrder: false },
            tenancyEndDate: {
                datesInWrongOrder: false,
                isTooShort: false,
                overSixMonthsAway: false,
                outsideDisputeWindow: false,
                tooCloseToWindowEnd: false,
            },
        },
        canSubmitForm: false,
        fieldHasErrors(fieldName) {
            // returns: boolean
            const fieldErrors = this.errors[fieldName];
            return Object.values(fieldErrors).some((value) => value === true);
        },
        formHasErrors() {
            // returns: boolean
            for (const field in this.errors) {
                const hasErrors = this.fieldHasErrors(field);
                if (hasErrors === true) {
                    return true;
                }
            }
            return false;
        },
        validationClassForField(fieldName) {
            // returns: string
            if (!!this.fields[fieldName]) {
                return this.fieldHasErrors(fieldName)
                    ? "is-invalid"
                    : "is-valid";
            }
            return "";
        },
        allRequiredFieldsHaveValues() {
            // returns: boolean
            const requiredFieldsValues = Object.values(this.fields);
            const someValueIsEmpty = requiredFieldsValues.some(
                (field) => field === "" || field === null,
            );
            return !someValueIsEmpty;
        },
        validateName() {
            // returns: null
            if (!this.fields.name) {
                return;
            }
            // normalise & trim spaces
            this.fields.name = this.fields.name.replace(/\s+/g, " ").trim();
            // match Unicode letters (\p{L}), spaces (\s), apostrophe (') or dash (-)
            const pattern = /^[\p{L}\s'-]+$/u;
            this.errors.name.isInvalid = !pattern.test(this.fields.name);
        },
        validateDepositAmount() {
            // returns: null
            if (!this.fields.depositAmount) {
                return;
            }
            this.errors.depositAmount.tooSmall =
                this.fields.depositAmount < 100;
        },
        daysBetweenDates(date1, date2) {
            // returns: number
            const diffInMs = date2 - date1;
            const msInDay = 1000 * 60 * 60 * 24;
            const diffInDays = Math.floor(diffInMs / msInDay);
            return diffInDays;
        },
        endDateIsInPast() {
            // returns: boolean
            return new Date(this.fields.tenancyEndDate) - new Date() < 0;
        },
        validateTenancyDates() {
            // returns: null
            if (!!this.fields.tenancyEndDate) {
                const tenancyEndDate = new Date(this.fields.tenancyEndDate);
                const today = new Date();
                const daysSinceEnd = this.daysBetweenDates(
                    tenancyEndDate,
                    today,
                );
                this.errors.tenancyEndDate.overSixMonthsAway =
                    daysSinceEnd < -180;
                this.errors.tenancyEndDate.outsideDisputeWindow =
                    daysSinceEnd > 90;
                this.errors.tenancyEndDate.tooCloseToWindowEnd =
                    daysSinceEnd > 85 && daysSinceEnd < 90;
            }

            if (!this.fields.tenancyStartDate || !this.fields.tenancyEndDate) {
                return;
            }

            const tenancyLength = this.daysBetweenDates(
                new Date(this.fields.tenancyStartDate),
                new Date(this.fields.tenancyEndDate),
            );
            const isWrongOrder = tenancyLength < 0;
            this.errors.tenancyStartDate.datesInWrongOrder = isWrongOrder;
            this.errors.tenancyEndDate.datesInWrongOrder = isWrongOrder;
            const isTooShort = 0 < tenancyLength && tenancyLength < 30;
            this.errors.tenancyStartDate.isTooShort = isTooShort;
            this.errors.tenancyEndDate.isTooShort = isTooShort;
        },
        validateForm() {
            // returns: null
            this.validateName();
            this.validateDepositAmount();
            this.validateTenancyDates();
            this.canSubmitForm =
                this.allRequiredFieldsHaveValues() && !this.formHasErrors();
        },
    };
}
