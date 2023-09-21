import pandas as pd
import re


class ValidationFailed(Exception):
    pass


class TransformData:
    def __init__(self, filepath: str, validate: bool = True) -> list:
        """Sets up the initial DataFrame from input CSV. Validates all input data against business ruling unless optional parameter validate is set to False."""
        self.filepath = filepath
        self.df = pd.pandas.read_csv(self.filepath, delimiter=";")
        self.df = self.df.applymap(
            lambda x: x.strip() if isinstance(x, str) else x  # Strip any whitespaces.
        )
        self.validate = validate
        self.new_data = []

    def IdCheck(self, id: str, row: object, index: int) -> str:
        """Validates IDs against business ruling using regex."""
        if not self.validate:
            return
        pattern = re.compile(
            "^[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}$"
        )

        if pattern.match(id) is None:
            raise ValidationFailed(
                f"One of your IDs failed regex validation. Make sure to follow this format (36 chars) and use A-Z or 0-9 characters: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.\n\nConflicting record (row {index + 2}):\n\n{row}."
            )

    def TimeStampCheck(self, timestamp: str, row: object, index: int) -> str:
        """Validates timestamps against business ruling using regex."""
        pattern = re.compile("^\d{4}-\d{2}-\d{2}T00:00:00\.000$")

        if pattern.match(timestamp) is None:
            raise ValidationFailed(
                f"One of your timestamps failed regex validation. Make sure to follow the format below (23 chars) and always use a time value of T00:00:00.000:\nYYYY-MM-DDT00:00:00.000.\n\nConflicting record (row {index + 2}):\n\n{row}."
            )

    def DataFrameValidation(self, dataframe: object) -> str:
        """Validates DataFrame against business ruling. Checks for empty mandatory fields."""
        if not self.validate:
            return
        if (
            dataframe.peopleMembershipId.isnull().values.any()
            or dataframe.paymentScheduleId.isnull().values.any()
            or dataframe.referenceDate.isnull().values.any()
        ):
            raise ValidationFailed(
                f"One of your records is missing a required field. Please correct your input.\n\nMandatory fields:\n\npeopleMembershipId\npaymentScheduleID\nreferenceDate"
            )

    def RowValidation(self, row: object, index: int) -> str:
        """Validates rows against business ruling. Checks if IDs and referenceDate are valid."""
        if not self.validate:
            return
        self.IdCheck(id=row.peopleMembershipId, row=row, index=index)

        self.IdCheck(id=row.paymentScheduleId, row=row, index=index)

        if pd.notna(row.promotionId):
            self.IdCheck(id=row.promotionId, row=row, index=index)

        self.TimeStampCheck(timestamp=row.referenceDate, row=row, index=index)

    def Output(self) -> list[dict]:
        """Transforms DataFrame to API calls."""

        self.DataFrameValidation(dataframe=self.df)

        for i, row in self.df.iterrows():
            self.RowValidation(row=row, index=i)

            if pd.notna(row.promotionId):
                url = f"https://trainmore-apiv6.gymmanager.eu/api/v1/PeopleMemberships/PeopleMembershipChange/{row.peopleMembershipId}/{row.paymentScheduleId}?referenceDate={row.referenceDate}&promotionId={row.promotionId}"
            else:
                url = f"https://trainmore-apiv6.gymmanager.eu/api/v1/PeopleMemberships/PeopleMembershipChange/{row.peopleMembershipId}/{row.paymentScheduleId}?referenceDate={row.referenceDate}"

            article_ids = []
            body = {}

            if pd.notna(row.article_id_1):
                article_ids.append(row.article_id_1)

            if pd.notna(row.article_id_2):
                article_ids.append(row.article_id_2)

            if pd.notna(row.article_id_3):
                article_ids.append(row.article_id_3)

            if pd.notna(row.article_id_4):
                article_ids.append(row.article_id_4)

            if pd.notna(row.article_id_5):
                article_ids.append(row.article_id_5)

            for id in article_ids:
                self.IdCheck(id=id, row=row, index=i)  # Validate article IDs

            if article_ids:
                body = {"articles": []}

                for id in article_ids:
                    body["articles"].append({"id": id, "metadata": "string"})

            self.new_data.append(
                {"ppl_mshp_id": row.peopleMembershipId, "url": url, "body": body}
            )

        return self.new_data

    def Report(self) -> str:
        """Returns report for processed records."""
        if self.validate:
            return f"{len(self.new_data)} records validated and ready to upload."
        else:
            return f"{len(self.new_data)} records ready to upload. Warning: Records are not validated."
